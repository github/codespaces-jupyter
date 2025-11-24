import React, { useState, useRef, useEffect } from 'react';
import { Camera, Volume2, RefreshCcw, HelpCircle } from 'lucide-react';

// 由於這是單一檔案，我們模擬一個簡單的翻譯與注音資料庫
// 實際上架版本通常會連接更強大的 Google Cloud Vision API
const OBJECT_DICTIONARY = {
  'person': { zh: '人', bopomofo: 'ㄖㄣˊ', sound: '人' },
  'cup': { zh: '杯子', bopomofo: 'ㄅㄟ ㄗ˙', sound: '杯子' },
  'cell phone': { zh: '手 機', bopomofo: 'ㄕㄡˇ ㄐㄧ', sound: '手機' },
  'keyboard': { zh: '鍵 盤', bopomofo: 'ㄐㄧㄢˋ ㄆㄢˊ', sound: '鍵盤' },
  'mouse': { zh: '滑 鼠', bopomofo: 'ㄏㄨㄚˊ ㄕㄨˇ', sound: '滑鼠' },
  'laptop': { zh: '筆 電', bopomofo: 'ㄅㄧˇ ㄉㄧㄢˋ', sound: '筆電' },
  'bottle': { zh: '瓶 子', bopomofo: 'ㄆㄧㄥˊ ㄗ˙', sound: '瓶子' },
  'cat': { zh: '貓 咪', bopomofo: 'ㄇㄠ ㄇㄧ', sound: '貓咪' },
  'dog': { zh: '小 狗', bopomofo: 'ㄒㄧㄠˇ ㄍㄡˇ', sound: '小狗' },
  'chair': { zh: '椅 子', bopomofo: 'ㄧˇ ㄗ˙', sound: '椅子' },
  'banana': { zh: '香 蕉', bopomofo: 'ㄒㄧㄤ ㄐㄧㄠ', sound: '香蕉' },
  'apple': { zh: '蘋 果', bopomofo: 'ㄆㄧㄥˊ ㄍㄨㄛˇ', sound: '蘋果' },
  'orange': { zh: '柳 丁', bopomofo: 'ㄌㄧㄡˇ ㄉㄧㄥ', sound: '柳丁' },
  'book': { zh: '書', bopomofo: 'ㄕㄨ', sound: '書' },
  'backpack': { zh: '背 包', bopomofo: 'ㄅㄟ ㄅㄠ', sound: '背包' },
  'teddy bear': { zh: '熊 熊', bopomofo: 'ㄒㄩㄥˊ ㄒㄩㄥˊ', sound: '熊熊' },
};

const App = () => {
  const videoRef = useRef(null);
  const [model, setModel] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [result, setResult] = useState(null); // { zh, bopomofo, type: 'success' | 'blur' | 'unknown' }
  const [cameraPermission, setCameraPermission] = useState(false);

  // 載入 TensorFlow.js MobileNet 模型
  useEffect(() => {
    const loadModel = async () => {
      try {
        // 動態載入 script，因為這是單一檔案環境
        if (!window.mobilenet) {
          await loadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest');
          await loadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@1.0.0'); 
        }
        const loadedModel = await window.mobilenet.load();
        setModel(loadedModel);
        setIsLoading(false);
      } catch (err) {
        console.error("模型載入失敗:", err);
        setIsLoading(false);
      }
    };
    loadModel();
  }, []);

  // 啟動相機
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // 優先使用後鏡頭
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraPermission(true);
      }
    } catch (err) {
      alert("無法啟動相機，請允許權限或使用手機瀏覽器開啟。");
    }
  };

  const loadScript = (src) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  // 文字轉語音 (TTS)
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // 停止之前的發音
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-TW';
      utterance.rate = 0.9; // 稍微放慢語速給小朋友聽
      utterance.pitch = 1.2; // 稍微高一點的聲音比較親切
      window.speechSynthesis.speak(utterance);
    }
  };

  const identifyObject = async () => {
    if (!model || !videoRef.current) return;

    // 清除上一次結果
    setResult(null);

    // 進行分類
    const predictions = await model.classify(videoRef.current);
    
    // 簡單的邏輯判斷
    if (predictions && predictions.length > 0) {
      const topPrediction = predictions[0];
      const className = topPrediction.className.toLowerCase().split(',')[0]; // 取第一個標籤
      const probability = topPrediction.probability;

      console.log(`Detected: ${className}, Confidence: ${probability}`);

      // 情況 2: 信心度太低 (太模糊或看不懂)
      if (probability < 0.2) {
        setResult({ type: 'blur', text: '太模糊囉' });
        speak("要拍清楚一點喔，再試一次看看");
        return;
      }

      // 檢查是否在我們的「兒童字典」中
      const data = OBJECT_DICTIONARY[className];

      if (data) {
        // 情況 1: 成功辨識
        setResult({ 
          type: 'success', 
          zh: data.zh, 
          bopomofo: data.bopomofo 
        });
        speak(`${data.sound}...這 是 ${data.sound}`);
      } else {
        // 情況 3: 辨識出物體，但不在字典內 (視為小朋友不該看或太難的東西)
        setResult({ type: 'unknown', text: '???' });
        speak("這個我也不知道，要問媽媽才知道");
      }
    } else {
      setResult({ type: 'blur', text: '沒看到東西' });
      speak("要拍清楚一點喔，再試一次看看");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-yellow-50 font-sans overflow-hidden">
      {/* 頂部標題列 */}
      <div className="bg-orange-400 p-4 shadow-md text-center z-10">
        <h1 className="text-xl font-bold text-white tracking-widest">AI 注音學習</h1>
      </div>

      {/* 中間相機區塊 */}
      <div className="flex-1 relative bg-black flex items-center justify-center overflow-hidden">
        {isLoading && (
          <div className="text-white animate-pulse">正在叫醒 AI 小精靈...</div>
        )}
        
        {!cameraPermission && !isLoading && (
          <button 
            onClick={startCamera}
            className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-full text-xl font-bold shadow-lg transform transition active:scale-95"
          >
            開啟相機
          </button>
        )}

        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          muted 
          className={`absolute w-full h-full object-cover ${!cameraPermission ? 'hidden' : ''}`}
        />

        {/* 掃描線動畫 (裝飾) */}
        {cameraPermission && !result && (
          <div className="absolute top-0 left-0 w-full h-1 bg-white opacity-50 shadow-[0_0_10px_white] animate-[scan_2s_linear_infinite]" />
        )}
      </div>

      {/* 下方 1/3 控制與顯示區 */}
      <div className="h-1/3 bg-white rounded-t-3xl -mt-6 z-20 shadow-[0_-5px_20px_rgba(0,0,0,0.1)] flex flex-col items-center p-4 relative">
        
        {/* 結果顯示區 */}
        <div className="flex-1 w-full flex flex-col items-center justify-center text-center">
          {result ? (
            <>
              {result.type === 'success' && (
                <div className="animate-bounce-short">
                  <div className="text-5xl font-bold text-gray-800 mb-2 font-mono tracking-widest">{result.bopomofo}</div>
                  <div className="text-3xl font-bold text-orange-500">{result.zh}</div>
                </div>
              )}
              {result.type === 'blur' && (
                <div className="text-gray-500 flex flex-col items-center">
                  <RefreshCcw size={48} className="mb-2" />
                  <p className="text-xl">看不清楚耶...</p>
                </div>
              )}
              {result.type === 'unknown' && (
                <div className="text-red-400 flex flex-col items-center">
                  <HelpCircle size={48} className="mb-2" />
                  <p className="text-xl">這是什麼呢？</p>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-400 text-lg">拍個東西讓我猜猜看！</p>
          )}
        </div>

        {/* 拍照按鈕 */}
        <div className="mb-2">
          <button 
            onClick={identifyObject}
            disabled={!cameraPermission || isLoading}
            className="w-20 h-20 bg-red-500 rounded-full border-4 border-white shadow-xl flex items-center justify-center active:bg-red-600 transform active:scale-90 transition-all disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <Camera size={40} className="text-white" />
          </button>
        </div>
        
        <p className="text-xs text-gray-300 mt-1">AI 辨識僅供參考</p>
      </div>

      {/* 掃描線動畫樣式 */}
      <style>{`
        @keyframes scan {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }
        .animate-bounce-short {
          animation: bounce 0.5s infinite alternate;
        }
        @keyframes bounce {
          from { transform: translateY(0); }
          to { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default App;
