import os
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Quantum-Relativistic Financial Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EngineConfig(BaseModel):
    num_states: int = 4
    beta: float = 0.01
    kappa: float = 0.1
    lyapunov_threshold: float = 4.20
    lambda_meta: float = 0.05
    lambda_cosmo: float = 0.1

class QuantumRelativisticEngine:
    def __init__(self, config: EngineConfig):
        self.N = config.num_states
        self.beta = config.beta
        self.kappa = config.kappa
        self.lyapunov_threshold = config.lyapunov_threshold
        self.lambda_meta = config.lambda_meta
        self.lambda_cosmo = config.lambda_cosmo
        
        self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)
        self.theta = np.random.randn(self.N) * 0.01  
        self.theta_0 = self.theta.copy()      
        
        self.norm_state = 1.0                 
        self.hilbert_reset_threshold = 5.0    

    def compute_relativistic_metric(self, price_change, volatility):
        kuhn_tucker_grad = price_change * volatility
        numerator = 1.0 + np.abs(kuhn_tucker_grad)**2
        denominator = 1.0 + self.beta * (self.norm_state**2)
        g_factor = numerator / denominator
        g_mu_nu = g_factor * np.array([-1.0, 1.0, 1.0, 1.0])
        return g_mu_nu, g_factor

    def compute_lyapunov_exponent(self, current_psi, previous_psi, dt=1):
        delta_psi = np.linalg.norm(current_psi - previous_psi)
        if delta_psi <= 1e-12:
            return 0.0
        jacobian_factor = np.abs(np.log(delta_psi / 1e-5) / dt)
        return jacobian_factor

    def compute_r_reg_tensor(self, g_mu_nu, lyapunov_exp, volatility, price_change):
        R_scalar = lyapunov_exp / self.lyapunov_threshold if self.lyapunov_threshold > 0 else 0.0
        T_mu_nu = np.diag([price_change, volatility, volatility, volatility])
        Lambda = self.lambda_cosmo
        kappa = self.kappa

        R_mu_nu_approx = np.diag([lyapunov_exp, lyapunov_exp, lyapunov_exp, lyapunov_exp])
        r_reg_tensor = R_mu_nu_approx - 0.5 * R_scalar * g_mu_nu + Lambda * g_mu_nu - kappa * T_mu_nu
        return r_reg_tensor

    def execute_meta_learning(self, current_loss, lr_meta=0.001):
        grad_theta = 2 * (self.theta - self.theta_0) * current_loss
        grad_theta = np.clip(grad_theta, -1.0, 1.0)
        self.theta -= lr_meta * grad_theta
        return np.sum(grad_theta**2)

    def step_evolution(self, price_change, volatility, target_value_normalized):
        prev_psi = self.c.copy()
        g_mu_nu, g_factor = self.compute_relativistic_metric(price_change, volatility)
        r_reg_tensor = self.compute_r_reg_tensor(g_mu_nu, self.lyapunov_threshold, volatility, price_change)
        regulation_factor = np.mean(np.abs(r_reg_tensor))

        phase_arg = np.clip(self.theta * g_factor * (1.0 - regulation_factor), -np.pi, np.pi)
        self.c = self.c * np.exp(1j * phase_arg)
        
        norm_c = np.linalg.norm(self.c)
        if norm_c > 0 and not np.isnan(norm_c):
            self.c /= norm_c
        else:
            self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)

        if np.linalg.norm(self.c) > self.hilbert_reset_threshold:
            self.c = np.ones(self.N, dtype=complex) / np.sqrt(self.N)
            self.norm_state = 1.0
        
        lyapunov_exp = self.compute_lyapunov_exponent(self.c, prev_psi)
        if np.isnan(lyapunov_exp) or np.isinf(lyapunov_exp):
            lyapunov_exp = 0.0
        
        if lyapunov_exp > self.lyapunov_threshold:
            self.norm_state += ((lyapunov_exp - self.lyapunov_threshold) * 0.1)
        else:
            self.norm_state = max(1.0, self.norm_state - 0.4 * (self.norm_state - 1.0))
            
        current_prediction = np.abs(self.c[0]) * target_value_normalized
        loss = 0.5 * (current_prediction - target_value_normalized)**2
        l_meta = self.execute_meta_learning(loss)
        
        return {
            "lyapunov": float(lyapunov_exp),
            "norm": float(self.norm_state),
            "loss": float(loss),
            "prediction_norm": float(current_prediction)
        }

@app.post("/simulate")
async def simulate(config: EngineConfig):
    try:
        ticker = "BTC-USD"
        raw_data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if raw_data.empty:
            raise HTTPException(status_code=404, detail="No data found for BTC-USD")
        
        if isinstance(raw_data.columns, pd.MultiIndex):
            raw_data.columns = raw_data.columns.get_level_values(0)
            
        close_prices = raw_data['Close'].values.astype(float).flatten()
        df = pd.DataFrame(index=raw_data.index)
        df['Price'] = close_prices
        df['Returns'] = df['Price'].pct_change().fillna(0)
        df['Volatility'] = df['Returns'].rolling(window=14).std().fillna(df['Returns'].std())
        max_historical_price = np.max(close_prices)
        df['Price_Normalized'] = df['Price'] / max_historical_price

        engine = QuantumRelativisticEngine(config)
        history = []
        
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            metrics = engine.step_evolution(
                price_change=row['Returns'],
                volatility=row['Volatility'],
                target_value_normalized=row['Price_Normalized']
            )
            history.append(metrics)

        # Calculate T+1 Boundaries
        last_close = float(df['Price'].iloc[-1])
        last_volatility = float(df['Volatility'].iloc[-1])
        last_norm = float(history[-1]['norm'])
        
        spatial_compression = 1.0 / last_norm
        max_tolerable_return = (config.lyapunov_threshold / (last_volatility * 10)) * spatial_compression
        
        upper_chaos_limit = last_close * (1.0 + max_tolerable_return)
        lower_chaos_limit = last_close * (1.0 - max_tolerable_return)

        return {
            "t_plus_1": {
                "upper_limit": upper_chaos_limit,
                "lower_limit": lower_chaos_limit,
                "max_tolerable_return": max_tolerable_return
            },
            "current_state": {
                "lyapunov": history[-1]['lyapunov'],
                "norm": last_norm,
                "last_price": last_close
            },
            "history": history[-20:] # Return last 20 steps for context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
