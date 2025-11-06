# 🧠Fine-Tuned Medical Assistant LLM API

An intelligent **Medical Assistant** powered by fine-tuning **Large Language Model (LLM)** that helps users answer medical-related questions with **reasoning-based explanations**.  
[The Med-Assistant LLM](https://huggingface.co/diyorarti/med-mixed-merged) is fine-tuned on the [dataset](https://huggingface.co/datasets/FreedomIntelligence/medical-o1-reasoning-SFT) and deployed as [a production-ready API](https://medical-assistant-c3n1.onrender.com) on Render.

---

## 🚀 Project Overview

This project aims to build a reliable **medical question & answerin through reasoning-based explanations** using a fine-tuned version of **Qwen/Qwen2.5-3B-Instruct**. The model provides **chain-of-thought** reasoning for complex medical queries, offering users both clear answers and transparent reasoning when applicable.

### **Training Objective:**  
A **mixed approach**:
- 70% of the training data contains **only the final answer**
- 30% includes **reasoning + final answer**

This combination helps the model balance concise answers with deeper reasoning capability.

---

## 🧩 Tech Stack

| Area | Tools / Libraries |
|------|--------------------|
| Model Fine-tuning | Hugging Face Transformers |
| Fine-tuning Method | LoRA (via PEFT) |
| Logging & Tracking | TensorBoard, Weights & Biases (wandb) |
| Environment | Google Colab (GPU) |
| API Development | FastAPI |
| Containerization | Docker |
| Deployment | Render (for API), Hugging Face Hub (for model) |

---

## 🧠 Model Details

- **Base model:** [Qwen/Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)  
- **Fine-tuned dataset:** [FreedomIntelligence/medical-o1-reasoning-SFT](https://huggingface.co/datasets/FreedomIntelligence/medical-o1-reasoning-SFT)  
- **Fine-tuned model:** [diyorarti/med-mixed-merged](https://huggingface.co/diyorarti/med-mixed-merged)
---

## 🔄 How the API Works

The Medical Assistant API connects a FastAPI backend with a fine-tuned Large Language Model (LLM) hosted on Hugging Face.

1. **User sends a request** → A client (like `curl`, Postman, or frontend app) sends a POST request to the `/v1/generate` or `/v1/chat/completions` endpoint with a medical query.
2. **API processes the input** → FastAPI receives the request and forwards the prompt to the Hugging Face Inference Endpoint using your `HF_API_TOKEN`.
3. **Model reasoning** → The fine-tuned model (`diyorarti/med-mixed-merged`) generates both reasoning steps and the final medical answer.
4. **Response returned** → The API formats the model’s output into JSON and sends it back to the user for display or further use.

📘 Example request:
```bash
# request
curl -X POST "https://medical-assistant-c3n1.onrender.com/v1/generate" \
-H "Content-Type: application/json" \
-d '{"prompt": "What are the early symptoms of diabetes?"}'

# llm answer 
{
  "response": "Early symptoms include frequent urination, excessive thirst, fatigue, and unexplained weight loss."
}
```

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/` | Home |
| `GET` | `/health` | Health check |
| `POST` | `/v1/generate` | Generate model output |
| `POST` | `/v1/chat/completions` | Chat completion endpoint |
---

## 🐳 Deployment

1. Fine-tuned model uploaded to Hugging Face Hub  
   🔗 [Model Link](https://huggingface.co/diyorarti/med-mixed-merged)

2. Model hosted on Hugging Face Inference Endpoints  
   🔗 [Inference Endpoint]() I can't share the endpoint URL due to security reasons. 

3. Production API developed using **FastAPI** and **Docker**, deployed to **Render**  
   🔗 [Live API](https://medical-assistant-c3n1.onrender.com) now, I have paused LLM. 

---

## 📸 Screenshot

![Swagger UI Screenshot](assets/render-api.png)
![Swagger UI Screenshot](assets/running-local.png)
![Swagger UI Screenshot](assets/api-generate-endpoint.png)
![Swagger UI Screenshot](assets/api-chat-completion-endpoint.png)

---


## 🧰 Installation & Setup (for local run)

```bash
# Clone the repository
git clone https://github.com/diyorarti/Medical-assistant.git
cd Medical-assistant

# Build Docker image
docker build -t medical-llm-api:latest .

# Run container
docker run --rm -p 8000:8000 -e HF_API_TOKEN=hf_******************************** -e API_KEY=****** medical-llm-api:latest
```

### NOTE
I have Paused HF-Endpoint, API generates when HF-Endpoint is on