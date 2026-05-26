import { useState, useEffect } from "react";
import ArticleCard from "../components/ArticleCard";
import { fetchTodaysArticles } from "../api";
import "./DigestPage.css";

export default function DigestPage() {
  const [sections, setSections] = useState({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchTodaysArticles();
        setSections(data.sections);
        setTotal(data.total);
      } catch (err) {
        setError("Loading your articles...");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="digest-state">
        <div className="digest-spinner" />
        <p>Loading today's news...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="digest-state">
        <p className="digest-error">{error}</p>
      </div>
    );
  }

  const categoryOrder = Object.keys(sections);

  return (
    <main className="digest-page">
      <header className="digest-header">
        <p className="digest-tagline">Your AI-curated daily briefing</p>
        <p className="digest-count">{total} articles across {categoryOrder.length} categories</p>
      </header>

      {categoryOrder.map((category, idx) => (
        <section key={category} className="digest-section">
          <div className="section-header">
            <h2 className="section-title">{category.toUpperCase()}</h2>
            <div className="section-line" />
            <span className="section-count">{sections[category].length} stories</span>
          </div>
          <div className="article-grid">
            {sections[category].map((article, i) => (
              <ArticleCard key={article.url || i} article={article} />
            ))}
          </div>
          {idx < categoryOrder.length - 1 && <div className="section-divider" />}
        </section>
      ))}
    </main>
  );
}