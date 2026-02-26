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

2. **Start Kafka (Local Setup)**:
   Ensure you have Kafka installed and running. 
   
   **Windows (PowerShell):**
   ```powershell
   # Start Zookeeper
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
   
   # Start Kafka Broker
   .\bin\windows\kafka-server-start.bat .\config\server.properties
   ```
   
   **Linux/macOS:**
   ```bash
   # Start Zookeeper
   bin/zookeeper-server-start.sh config/zookeeper.properties
   
   # Start Kafka Broker
   bin/kafka-server-start.sh config/server.properties
   ```

3. **Set OpenAI API Key**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Run the Integrated System**:
   The `main.py` script will automatically start the producer, streaming engine, and web interface.
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
