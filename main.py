# ==============================================================================
# CELDA 1: ENTORNO, DEPENDENCIAS E IMPORTACIONES GENERALES
# ==============================================================================
import os
import numpy as np
import pandas as pd
import yfinance as yf

# Configuración de graficación para soporte headless / entornos de servidor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

print("[+] Entorno e importaciones inicializadas correctamente.")

# ==============================================================================
# CELDA 2: ARQUITECTURA DEL MOTOR GEOMÉTRICO (LYAPUNOV & META-LEARNING)
# ==============================================================================
class QuantumRelativisticEngine:
    def __init__(self, num_states=4, beta=0.01, kappa=0.1, lyapunov_threshold=4.20, lambda_meta=0.05):
        self.N = num_states
        self.beta = beta                  # Coeficiente de autointeracción relativista
        self.kappa = kappa                # Constante de acoplamiento de control
        self.lyapunov_threshold = lyapunov_threshold  # Umbral crítico de caos reajustado
        self.lambda_meta = lambda_meta    # Regularización para el espacio Meta-Learning
        
        # Inicialización del Espacio de Hilbert H (Ground State)
        self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)
        self.theta = np.random.randn(self.N) * 0.01  
        self.theta_0 = self.theta.copy()      
        
        # Inicialización del Bloque de Memorias Adaptativas
        self.MP = np.random.rand(self.N) * 0.01
        self.MR = np.zeros(self.N)            
        self.norm_state = 1.0                 # Estado base de la Norma L2
        self.alpha = 0.5                      # Balance de peso de peso de memoria (t)
        self.hilbert_reset_threshold = 5.0    # Umbral de Safety Layer para la norma de Hilbert

    def compute_relativistic_metric(self, price_change, volatility):
        """
        Calcula la métrica g_μν basada en el cambio de precio y la volatilidad local.
        """
        kuhn_tucker_grad = price_change * volatility
        numerator = 1.0 + np.abs(kuhn_tucker_grad)**2
        denominator = 1.0 + self.beta * (self.norm_state**2)
        g_factor = numerator / denominator
        
        g_mu_nu = g_factor * np.array([-1.0, 1.0, 1.0, 1.0])
        return g_mu_nu, g_factor

    def compute_lyapunov_exponent(self, current_psi, previous_psi, dt=1):
        """
        Aproxima el Exponente de Lyapunov local midiendo la divergencia geométrica.
        """
        delta_psi = np.linalg.norm(current_psi - previous_psi)
        if delta_psi <= 1e-12:
            return 0.0
        jacobian_factor = np.abs(np.log(delta_psi / 1e-5) / dt)
        return jacobian_factor

    def compute_r_reg_tensor(self, g_mu_nu, lyapunov_exp, volatility, price_change):
        """
        Implementa el tensor de regularización R_reg basado en una aproximación
        de la ecuación de Einstein R_μν - 1/2 R g_μν + Λg_μν = κT_μν + R_reg.
        Se asume un tensor de energía-momento (T_μν) y curvatura escalar (R)
        simplificados para fines de regularización.
        """
        # Simplificación: Curvatura escalar (R) como función del caos/estabilidad
        R_scalar = lyapunov_exp / self.lyapunov_threshold if self.lyapunov_threshold > 0 else 0.0

        # Simplificación: Tensor de energía-momento (T_μν) como función del mercado
        T_mu_nu = np.diag([price_change, volatility, volatility, volatility])
        
        # Constantes (aproximadas)
        Lambda = 0.1  # Constante cosmológica (regularización de fondo)
        kappa = 0.5   # Constante de acoplamiento gravitacional

        # Ecuación de Einstein simplificada para R_reg:
        # R_reg = R_μν - 1/2 R g_μν + Λg_μν - κT_μν
        # Aquí R_μν se aproxima como una función de Lyapunov
        R_mu_nu_approx = np.diag([lyapunov_exp, lyapunov_exp, lyapunov_exp, lyapunov_exp])
        
        r_reg_tensor = R_mu_nu_approx - 0.5 * R_scalar * g_mu_nu + Lambda * g_mu_nu - kappa * T_mu_nu
        return r_reg_tensor

    def execute_meta_learning(self, current_loss, lr_meta=0.001):
        """
        Meta-Learning de segundo orden estabilizado mediante Gradient Clipping.
        """
        grad_theta = 2 * (self.theta - self.theta_0) * current_loss
        grad_theta = np.clip(grad_theta, -1.0, 1.0)  # Prevención de explosión
        
        l_meta = np.sum(grad_theta**2) + self.lambda_meta * np.sum((self.theta - self.theta_0)**2)
        self.theta -= lr_meta * grad_theta
        return l_meta

    def random_walk_memory_update(self):
        """
        Implementa una caminata aleatoria para la actualización de los estados cuánticos.
        (Basado en la sección 1.8 del documento técnico - asunción al no ser provista)
        Esto permite una exploración del espacio de Hilbert cuando el sistema es estable.
        """
        if self.norm_state < self.lyapunov_threshold: # Solo si no hay caos
            random_perturbation = (np.random.rand(self.N) - 0.5) * 0.01 + 1j * (np.random.rand(self.N) - 0.5) * 0.01
            self.c = self.c * np.exp(random_perturbation)
            norm_c = np.linalg.norm(self.c)
            if norm_c > 0 and not np.isnan(norm_c):
                self.c /= norm_c

    def step_evolution(self, price_change, volatility, target_value_normalized):
        """
        Evolución temporal continua utilizando variables normalizadas unitarias.
        """
        prev_psi = self.c.copy()
        
        # 1. Espacio métrico relativista
        g_mu_nu, g_factor = self.compute_relativistic_metric(price_change, volatility)
        
        # 2. Cálculo del tensor de regularización R_reg
        r_reg_tensor = self.compute_r_reg_tensor(g_mu_nu, engine.lyapunov_threshold, volatility, price_change)
        # Se aplica la regularización al factor de fase para controlar la evolución
        # La forma exacta de aplicar R_reg puede variar, aquí se usa para modular phase_arg
        regulation_factor = np.mean(np.abs(r_reg_tensor)) # Promedio de la magnitud del tensor

        phase_arg = np.clip(self.theta * g_factor * (1.0 - regulation_factor), -np.pi, np.pi)
        self.c = self.c * np.exp(1j * phase_arg)
        
        # Proyección y normalización estricta en el espacio de Hilbert
        norm_c = np.linalg.norm(self.c)
        if norm_c > 0 and not np.isnan(norm_c):
            self.c /= norm_c
        else:
            self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)

        # SAFETY LAYER: Reset de Hilbert si la norma supera el umbral
        if np.linalg.norm(self.c) > self.hilbert_reset_threshold:
            self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N) # Reset al Ground State
            self.norm_state = 1.0 # Reset de la norma también
            status_safety = "❌ HILBERT RESET: Norma L2 excedida. Reiniciando a Ground State."
        else:
            status_safety = ""
        
        lyapunov_exp = self.compute_lyapunov_exponent(self.c, prev_psi)
        if np.isnan(lyapunov_exp) or np.isinf(lyapunov_exp):
            lyapunov_exp = 0.0
        
        # Lógica de absorción elástica por Norma L2 (ahora influenciada por R_reg)
        if lyapunov_exp > self.lyapunov_threshold:
            self.norm_state += ((lyapunov_exp - self.lyapunov_threshold) * 0.1)  # Amortiguación suave
            status = "⚠️  CHAOS DETECTED"
        else:
            # Enfriamiento dinámico acelerado hacia el Ground State (1.0)
            self.norm_state = max(1.0, self.norm_state - 0.4 * (self.norm_state - 1.0))
            status = "✅ STABLE"
            # Optimización de Memoria: Caminata aleatoria en estados cuánticos
            self.random_walk_memory_update()
            
        # 4. Evaluación del Error en escala controlada [0, 1]
        current_prediction = np.abs(self.c[0]) * target_value_normalized
        loss = 0.5 * (current_prediction - target_value_normalized)**2
        
        # 5. Ejecución del ciclo de Meta-Learning
        l_meta = self.execute_meta_learning(loss)
        
        # 6. Actualización dinámica del bloque de memoria M(t)
        success_condition = 1.0 if loss < 0.01 else 0.0
        if success_condition == 1.0:
            self.alpha = max(0.1, self.alpha - 0.05)
            self.MR += 0.01 * np.abs(self.c)
        else:
            self.alpha = min(0.9, self.alpha + 0.05)
            self.MP += 0.01 * self.theta
            
        # 7. Actualización del aprendizaje estándar con protección anti-explosión
        grad_loss = np.clip(self.theta_0 * loss, -0.1, 0.1)
        self.theta_0 -= 0.01 * grad_loss
        
        final_status = f"{status} {status_safety}".strip()

        return {
            "Lyapunov": lyapunov_exp,
            "Norm": self.norm_state,
            "Status": final_status,
            "Loss": loss,
            "L_Meta": l_meta,
            "Prediction_Norm": current_prediction
        }

# ==============================================================================
# CELDA 3: PIPELINE DE INGESTA DE DATOS Y NORMALIZACIÓN DE MATRIZ
# ==============================================================================
print("[*] Conectando a los servidores de Yahoo Finance para obtener BTC-USD...")
ticker = "BTC-USD"

raw_data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)

if raw_data.empty:
    raise ValueError("[-] Error crítico: No se recibieron datos históricos.")

if isinstance(raw_data.columns, pd.MultiIndex):
    raw_data.columns = raw_data.columns.get_level_values(0)

close_prices = raw_data['Close'].values.astype(float).flatten()
dates = raw_data.index

df = pd.DataFrame(index=dates)
df['Price'] = close_prices
df['Returns'] = df['Price'].pct_change().fillna(0)
df['Volatility'] = df['Returns'].rolling(window=14).std().fillna(df['Returns'].std())

# Estabilización numérica crítica
max_historical_price = np.max(close_prices)
df['Price_Normalized'] = df['Price'] / max_historical_price

print(f"[+] Ingesta exitosa. Punto máximo de escala de referencia: ${max_historical_price:.2f} USD")

# ==============================================================================
# CELDA 4: BUCLE CONTINUO EN TIEMPO REAL
# ==============================================================================
engine = QuantumRelativisticEngine(num_states=4, lyapunov_threshold=4.20)
history = []

print("=" * 100)
for idx, (timestamp, row) in enumerate(df.iterrows()):
    metrics = engine.step_evolution(
        price_change=row['Returns'],
        volatility=row['Volatility'],
        target_value_normalized=row['Price_Normalized']
    )
    
    real_prediction = metrics["Prediction_Norm"] * max_historical_price
    
    history.append({
        "Price": row['Price'],
        "Lyapunov": metrics["Lyapunov"],
        "Norm": metrics["Norm"],
        "Loss": metrics["Loss"],
        "L_Meta": metrics["L_Meta"],
        "Prediction": real_prediction,
        "Status": metrics["Status"]
    })
    
    if idx % 15 == 0:
        date_str = timestamp.strftime('%Y-%m-%d')
        print(f"{date_str} | Price: $ {row['Price']:9.2f} | Lyapunov: {metrics['Lyapunov']:.6f} | Norm: {metrics['Norm']:.4f} | {metrics['Status']}")

print("=" * 100)
df_res = pd.DataFrame(history, index=df.index)
print("[+] Simulación temporal sin desbordamiento finalizada con éxito.")

# ==============================================================================
# CELDA 5: CAPA PREDICTIVA EN T+1 Y LÍMITES DE FRONTERA DINÁMICOS
# ==============================================================================
last_close = df_res['Price'].iloc[-1]
last_volatility = df['Volatility'].iloc[-1]
last_norm = df_res['Norm'].iloc[-1]

spatial_compression = 1.0 / last_norm
max_tolerable_return = (engine.lyapunov_threshold / (last_volatility * 10)) * spatial_compression

upper_chaos_limit = last_close * (1.0 + max_tolerable_return)
lower_chaos_limit = last_close * (1.0 - max_tolerable_return)

print("\n[*] Inicializando análisis predictivo del próximo ciclo de mercado...")
print("=" * 100)
print(f"MÉTRICAS BASE EN T (ÚLTIMO CIERRE REGISTRADO):")
print(f"  -> Último Precio de Cierre ($S_t$) : ${last_close:.2f} USD")
print(f"  -> Volatilidad del Sistema (\\sigma_t) : {last_volatility:.6f}")
print(f"  -> Magnitud de la Norma L2 (||\\psi||) : {last_norm:.4f}")
print("-" * 100)
print("PROYECCIÓN PREDICTIVA PARA T+1 (PRÓXIMAS 24 HORAS):")
print(f"  -> Retorno Crítico Máximo Tolerable: ±{max_tolerable_return*100:.2f}%")
print(f"  -> LÍMITE SUPERIOR DE CAOS         : ${upper_chaos_limit:.2f} USD")
print(f"  -> LÍMITE INFERIOR DE CAOS         : ${lower_chaos_limit:.2f} USD")
print(f"  -> CRÍTICO AJUSTADO POR NORMA    : ${lower_chaos_limit * spatial_compression:.2f} USD")
print("=" * 100)

if last_norm == 1.0:
    print("✅ SISTEMA EN EQUILIBRIO: Las fronteras predictivas operan dentro de los márgenes estándar.")
else:
    print("⚠️  VARIEDAD DEFORMADA: Espacio elástico adaptado por la persistencia de energía caótica.")
print("=" * 100)

# ==============================================================================
# CELDA 6: RENDERIZADO ANALÍTICO DEL ESPACIO DE FASES
# ==============================================================================
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# 1. Gráfico del espacio de variables físico
axs[0].plot(df_res.index, df_res['Price'], label="Precio BTC-USD (Cierre Real)", color='cyan', lw=2)
axs[0].set_title("Evolución del Espacio de Variables Real", fontsize=12, color='white')
axs[0].set_ylabel("Precio (USD)", color='white')
axs[0].grid(True, alpha=0.15)
axs[0].legend(loc="upper left")

# 2. Exponente de Lyapunov local frente al umbral crítico
axs[1].plot(df_res.index, df_res['Lyapunov'], label="Exponente Lyapunov Local (λ)", color='magenta', alpha=0.7)
axs[1].axhline(y=engine.lyapunov_threshold, color='red', linestyle='--', label="Umbral de Caos Configurado")
axs[1].set_title("Métrica de Divergencia Exponencial (Control de Caos)", fontsize=12, color='white')
axs[1].set_ylabel("Magnitud λ", color='white')
axs[1].grid(True, alpha=0.15)
axs[1].legend(loc="upper left")

# 3. Gráfico de deformación elástica de la Norma L2 en Hilbert
axs[2].plot(df_res.index, df_res['Norm'], label="Deformación Dinámica de la Norma L2", color='yellow', lw=2)
axs[2].set_title("Estado Topológico del Espacio de Hilbert (Resiliencia Manifold)", fontsize=12, color='white')
axs[2].set_ylabel("Valor de la Norma", color='white')
axs[2].set_xlabel("Línea Temporal de la Simulación", color='white')
axs[2].grid(True, alpha=0.15)
axs[2].legend(loc="upper left")

# Aplicación de estilo científico Dark-Mode
for ax in axs:
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white')
fig.patch.set_facecolor('#1a1a1a')

plt.tight_layout()
output_filename = "panel_estabilidad_fase.png"
plt.savefig(output_filename, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
print(f"[+] Panel geométrico exportado con éxito en alta resolución: '{output_filename}'\n")
