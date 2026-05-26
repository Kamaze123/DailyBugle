import { useState } from "react";
import "./ArticleCard.css";

export default function ArticleCard({ article }) {
  const [expanded, setExpanded] = useState(false);

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <article
      className={`article-card ${expanded ? "expanded" : ""}`}
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
    >
      <div className="article-meta">
        <span className="article-source">{article.source}</span>
        <span className="article-dot">·</span>
        <span className="article-date">{formatDate(article.published_at)}</span>
      </div>
      <h3 className="article-title">{article.title}</h3>
      <p className={`article-summary ${expanded ? "full" : ""}`}>
        {article.summary || article.description || "No summary available."}
      </p>
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="article-link"
      >
        Read full article ↗
      </a>
    </article>
  );
}