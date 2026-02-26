# EcoPulse AI - Real-Time Environmental Intelligence

EcoPulse AI is a production-grade smart-city intelligence system that monitors environmental health in real-time using Pathway's streaming engine and Kafka.

## 🏗 Architecture
- **Kafka**: Simulated environmental sensor stream.
- **Pathway**: High-performance streaming feature engineering and anomaly detection.
- **Flask**: Enterprise-grade API and multi-page UI.
- **Climate Copilot**: LLM-powered scientific advisor for environmental safety.

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Kafka is Running**:
   The system expects a Kafka broker at `localhost:9092`.

3. **Set OpenAI API Key**:
   Create a `.env` file with `OPENAI_API_KEY=your_key`.

4. **Run the System**:
   ```bash
   python main.py
   ```

## 🌐 Features
- **Live Dashboard**: Real-time AQI, PM2.5, and CO2 monitoring.
- **Advanced Analytics**: Momentum and volatility tracking using Pathway.
- **Climate Copilot**: AI-driven insights into environmental risks.
- **Incident Reports**: Historical log of anomalies.

## 🛠 Tech Stack
- **Streaming**: Pathway
- **Broker**: Kafka
- **Backend**: Flask
- **Frontend**: HTML5, TailwindCSS, Chart.js
- **Intelligence**: OpenAI GPT-4o
