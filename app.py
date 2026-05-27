import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(page_title="Quantum Relativistic Engine", layout="wide", page_icon="🌌")
st.title("🌌 Panel de Control: Motor Cuántico-Relativista")
st.markdown("Plataforma de pruebas *offline* para el análisis de estabilidad y control de caos en series financieras.")

# ==============================================================================
# CLASE DEL MOTOR (Integrada para portabilidad del orquestador)
# ==============================================================================
class QuantumRelativisticEinsteinEngine:
    def __init__(self, num_states=4, beta=0.01, kappa=0.1, base_threshold=2.0, lambda_meta=0.05, Lambda_cosmo=0.02):
        self.N = num_states
        self.beta = beta                  
        self.kappa = kappa                
        self.Lambda = Lambda_cosmo        
        self.base_threshold = base_threshold  
        self.lambda_meta = lambda_meta    
        
        self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)
        self.theta = np.random.randn(self.N) * 0.01  
        self.theta_0 = self.theta.copy()      
        
        self.MP = np.random.rand(self.N) * 0.01
        self.MR = np.zeros(self.N)            
        self.norm_state = 1.0                 
        self.lyapunov_window = []

    def compute_einstein_tensor_control(self, price_change, volatility):
        kuhn_tucker_grad = price_change * volatility
        numerator = 1.0 + np.abs(kuhn_tucker_grad)**2
        denominator = 1.0 + self.beta * (self.norm_state**2)
        g_factor = numerator / denominator
        g_mu_nu = g_factor * np.array([-1.0, 1.0, 1.0, 1.0])
        
        partial_mu_psi = np.array([price_change, volatility, np.abs(self.c[0]), np.mean(self.theta)])
        lagrangian = 0.5 * np.sum(partial_mu_psi[1:]**2) - 0.5 * (price_change**2)
        
        T_mu_nu = np.zeros(4)
        for mu in range(4):
            T_mu_nu[mu] = (partial_mu_psi[mu] * partial_mu_psi[mu]) - (g_mu_nu[mu] * lagrangian)
            
        trace_T = np.sum(T_mu_nu * (1.0 / g_mu_nu))
        R_scalar = -self.kappa * trace_T + 4.0 * self.Lambda
        R_mu_nu = self.kappa * (T_mu_nu - 0.5 * trace_T * g_mu_nu) + self.Lambda * g_mu_nu
        R_reg = R_mu_nu - 0.5 * R_scalar * g_mu_nu + self.Lambda * g_mu_nu
        
        return g_mu_nu, g_factor, np.mean(R_reg)

    def compute_lyapunov_exponent(self, current_psi, previous_psi):
        delta_psi = np.linalg.norm(current_psi - previous_psi)
        if delta_psi <= 1e-12: return 0.0
        return np.abs(np.log(delta_psi + 1e-8))

    def execute_meta_learning(self, current_loss, lr_meta=0.001):
        grad_theta = 2 * (self.theta - self.theta_0) * current_loss
        grad_theta = np.clip(grad_theta, -1.0, 1.0)
        l_meta = np.sum(grad_theta**2) + self.lambda_meta * np.sum((self.theta - self.theta_0)**2)
        self.theta -= lr_meta * grad_theta
        return l_meta

    def step_evolution(self, price_change, volatility, target_value_normalized):
        prev_psi = self.c.copy()
        g_mu_nu, g_factor, r_reg_scalar = self.compute_einstein_tensor_control(price_change, volatility)
        
        phase_arg = np.clip(self.theta * g_factor + (r_reg_scalar * self.kappa), -np.pi, np.pi)
        self.c = self.c * np.exp(1j * phase_arg)
        
        norm_c = np.linalg.norm(self.c)
        if norm_c > 0 and not np.isnan(norm_c): self.c /= norm_c
        else: self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)
        
        lyapunov_exp = self.compute_lyapunov_exponent(self.c, prev_psi)
        if np.isnan(lyapunov_exp) or np.isinf(lyapunov_exp): lyapunov_exp = 0.0
            
        self.lyapunov_window.append(lyapunov_exp)
        if len(self.lyapunov_window) > 14: self.lyapunov_window.pop(0)
            
        dynamic_threshold = np.mean(self.lyapunov_window) + (1.5 * np.std(self.lyapunov_window) if len(self.lyapunov_window) > 2 else 0)
        if dynamic_threshold <= 0: dynamic_threshold = self.base_threshold
        
        # Guardrail de seguridad: Reinicio de Hilbert
        if self.norm_state > 5.0:
            self.norm_state = 1.0
            
        if lyapunov_exp > dynamic_threshold:
            self.norm_state += ((lyapunov_exp - dynamic_threshold) * 0.05)  
            status = "⚠️ CAOS"
        else:
            self.norm_state = max(1.0, self.norm_state - 0.3 * (self.norm_state - 1.0))
            status = "✅ ESTABLE"
            
        current_prediction = np.abs(self.c[0]) * target_value_normalized
        loss = 0.5 * (current_prediction - target_value_normalized)**2
        
        l_meta = self.execute_meta_learning(loss)
        
        if loss < 0.01: self.MR += 0.01 * np.abs(self.c)
        else: self.MP += 0.01 * self.theta
            
        grad_loss = np.clip(self.theta_0 * loss, -0.1, 0.1)
        self.theta_0 -= 0.01 * grad_loss
        
        return {
            "Lyapunov": lyapunov_exp, "Threshold": dynamic_threshold,
            "Norm": self.norm_state, "Status": status, "Loss": loss,
            "L_Meta": l_meta, "Prediction_Norm": current_prediction,
            "R_reg_scalar": r_reg_scalar
        }

# ==============================================================================
# INTERFAZ DE USUARIO (UI)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Hiperparámetros")
    ticker_input = st.text_input("Activo (Ticker)", value="BTC-USD")
    period_input = st.selectbox("Periodo Histórico", ["3mo", "6mo", "1y", "2y"], index=1)
    
    st.markdown("---")
    beta_param = st.slider("Beta (Autointeracción)", 0.001, 0.1, 0.01, 0.001)
    kappa_param = st.slider("Kappa (Acoplamiento de Campo)", 0.01, 0.5, 0.1, 0.01)
    lambda_param = st.slider("Λ (Constante Cosmológica)", 0.01, 0.1, 0.02, 0.01)
    
    run_button = st.button("🚀 Ejecutar Simulación", type="primary", use_container_width=True)

if run_button:
    with st.spinner(f"Descargando datos de {ticker_input} e inicializando tensores..."):
        # 1. Ingesta de Datos
        raw_data = yf.download(ticker_input, period=period_input, interval="1d", auto_adjust=True)
        if isinstance(raw_data.columns, pd.MultiIndex):
            raw_data.columns = raw_data.columns.get_level_values(0)
            
        close_prices = raw_data['Close'].values.astype(float).flatten()
        dates = raw_data.index
        df = pd.DataFrame(index=dates)
        df['Price'] = close_prices
        df['Returns'] = df['Price'].pct_change().fillna(0)
        df['Volatility'] = df['Returns'].rolling(window=14).std().fillna(df['Returns'].std())
        max_historical_price = np.max(close_prices)
        df['Price_Normalized'] = df['Price'] / max_historical_price

        # 2. Orquestación del Bucle Matemático
        engine = QuantumRelativisticEinsteinEngine(
            beta=beta_param, kappa=kappa_param, Lambda_cosmo=lambda_param, base_threshold=2.0
        )
        
        history = []
        progress_bar = st.progress(0)
        
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            metrics = engine.step_evolution(row['Returns'], row['Volatility'], row['Price_Normalized'])
            history.append({
                "Date": timestamp, "Price": row['Price'],
                "Lyapunov": metrics["Lyapunov"], "Threshold": metrics["Threshold"],
                "Norm": metrics["Norm"], "R_reg": metrics["R_reg_scalar"],
                "Status": metrics["Status"]
            })
            progress_bar.progress((idx + 1) / len(df))
            
        df_res = pd.DataFrame(history).set_index("Date")

        # 3. Cálculo Predictivo T+1
        last_close = df_res['Price'].iloc[-1]
        last_volatility = df['Volatility'].iloc[-1]
        last_norm = df_res['Norm'].iloc[-1]
        last_threshold = df_res['Threshold'].iloc[-1]
        spatial_compression = 1.0 / last_norm
        raw_return_factor = (last_threshold * last_volatility) * spatial_compression
        max_tolerable_return = np.tanh(raw_return_factor * 10) * 0.20  
        
        upper_chaos_limit = last_close * (1.0 + max_tolerable_return)
        lower_chaos_limit = last_close * (1.0 - max_tolerable_return)
        critical_adjusted = last_close * spatial_compression

    # ==============================================================================
    # RENDERIZADO DEL DASHBOARD
    # ==============================================================================
    st.success("Simulación finalizada sin desbordamientos numéricos.")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Último Precio (T)", f"${last_close:,.2f}")
    col2.metric("Límite Superior Caos (T+1)", f"${upper_chaos_limit:,.2f}")
    col3.metric("Límite Inferior Caos (T+1)", f"${lower_chaos_limit:,.2f}")
    col4.metric("Estado Geométrico (Norma)", f"{last_norm:.4f}", 
                delta="Equilibrio" if last_norm <= 1.05 else "Deformado", delta_color="inverse")

    # Gráficos con Matplotlib
    st.subheader("Análisis de Espacio de Fases")
    
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    # Precio
    axs[0].plot(df_res.index, df_res['Price'], label=f"Precio {ticker_input}", color='#00d4ff', lw=2)
    axs[0].axhline(y=upper_chaos_limit, color='#ff4b4b', linestyle=':', alpha=0.6, label="Frontera Superior (T+1)")
    axs[0].axhline(y=lower_chaos_limit, color='#ffa500', linestyle=':', alpha=0.6, label="Frontera Inferior (T+1)")
    axs[0].set_title("Evolución del Espacio de Variables Real", color='white')
    axs[0].legend(loc="upper left")
    
    # R_reg
    axs[1].plot(df_res.index, df_res['R_reg'], label="Tensor Regularizador de Curvatura (R_reg)", color='#ffcc00', lw=1.5)
    axs[1].axhline(y=0, color='white', linestyle='--', alpha=0.3)
    axs[1].set_title("Inyección de Amortiguación Relativista", color='white')
    axs[1].legend(loc="upper left")
    
    # Norma
    axs[2].plot(df_res.index, df_res['Norm'], label="Resiliencia Topológica (Norma L2)", color='#00ff00', lw=2)
    axs[2].set_title("Estado del Espacio de Hilbert", color='white')
    axs[2].legend(loc="upper left")

    for ax in axs:
        ax.set_facecolor('#0e1117')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.1)
    fig.patch.set_facecolor('#0e1117')
    plt.tight_layout()
    
    st.pyplot(fig)

    with st.expander("Ver Datos Tabulares de Diagnóstico"):
        st.dataframe(df_res.tail(20).style.applymap(
            lambda x: 'color: red' if 'CAOS' in str(x) else ('color: green' if 'ESTABLE' in str(x) else ''),
            subset=['Status']
        ))
else:
    st.info("👈 Configura los parámetros en el panel lateral y haz clic en 'Ejecutar Simulación' para comenzar.")
