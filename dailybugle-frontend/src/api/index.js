import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export const fetchGroupedArticles = async () => {
  const res = await api.get("/articles/grouped");
  return res.data;
};

export const askQuestion = async (question) => {
  const res = await api.post("/ask", { question });
  return res.data;
};

export const runPipeline = async () => {
  const res = await api.post("/pipeline/run");
  return res.data;
};

export const fetchCategories = async () => {
  const res = await api.get("/categories");
  return res.data;
};