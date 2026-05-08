const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function generateStory(payload) {
  const response = await fetch(`${API_BASE_URL}/api/generate-story`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Story generation failed. Please try again.");
  }

  return data;
}
