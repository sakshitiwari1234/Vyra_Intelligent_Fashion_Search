import { useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Check,
  ChevronRight,
  ImagePlus,
  LoaderCircle,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Zap,
} from "lucide-react";

import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const fileInputRef = useRef(null);

  const [query, setQuery] = useState("something similar but black");
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");

  const constraints = useMemo(() => {
    if (!response?.final_intent) return [];

    const intent = response.final_intent;
    const items = [];

    if (intent.category) {
      items.push({
        label: "Category",
        value: intent.category,
      });
    }

    if (intent.colours?.length) {
      items.push({
        label: "Colour",
        value: intent.colours.join(", "),
      });
    }

    if (intent.gender) {
      items.push({
        label: "Gender",
        value: intent.gender,
      });
    }

    if (intent.max_price) {
      items.push({
        label: "Max price",
        value: `₹${intent.max_price}`,
      });
    }

    if (intent.min_price) {
      items.push({
        label: "Min price",
        value: `₹${intent.min_price}`,
      });
    }

    if (intent.pattern) {
      items.push({
        label: "Pattern",
        value: intent.pattern,
      });
    }

    return items;
  }, [response]);

  const handleFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please upload a valid fashion image.");
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResponse(null);
    setError("");
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDragActive(false);

    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  };

  const removeImage = () => {
    setImage(null);
    setPreview("");
    setResponse(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const searchProducts = async () => {
    if (!image) {
      setError("Upload a reference image first.");
      return;
    }

    if (!query.trim()) {
      setError("Tell VYRA what you are looking for.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);

    const form = new FormData();

    form.append("query", query.trim());
    form.append("image", image);
    form.append("top_k", "6");

    try {
      const result = await fetch(
        `${API_BASE}/search/multimodal`,
        {
          method: "POST",
          body: form,
        }
      );

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data?.detail || "Search failed."
        );
      }

      setResponse(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the VYRA backend."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="nav-inner">
          <div className="brand">
            <div className="brand-mark">
              V
            </div>

            <div>
              <div className="brand-name">
                VYRA
              </div>
              <div className="brand-sub">
                Intelligent Fashion Search
              </div>
            </div>
          </div>

          <div className="nav-center">
            <span>Discover</span>
            <span>How it works</span>
            <span>AI Search</span>
          </div>

          <div className="nav-badge">
            <Sparkles size={15} />
            Multimodal AI
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-glow glow-one" />
          <div className="hero-glow glow-two" />

          <div className="hero-content">
            <div className="eyebrow">
              <Sparkles size={14} />
              Constraint-safe fashion discovery
            </div>

            <h1>
              Find what you mean,
              <br />
              <span>not just what you type.</span>
            </h1>

            <p>
              Upload an inspiration image, describe
              what you want to change, and let VYRA
              combine visual understanding, semantic
              search, and strict shopping constraints.
            </p>

            <div className="hero-trust">
              <div>
                <BrainCircuit size={17} />
                Visual understanding
              </div>

              <div>
                <ShieldCheck size={17} />
                Constraint validation
              </div>

              <div>
                <Zap size={17} />
                Hybrid AI ranking
              </div>
            </div>
          </div>
        </section>

        <section className="workspace">
          <div className="workspace-heading">
            <div>
              <span className="section-kicker">
                AI SEARCH
              </span>

              <h2>
                Start with an image.
                Refine with language.
              </h2>
            </div>

            <div className="step-label">
              <span>01</span>
              Search workspace
            </div>
          </div>

          <div className="search-layout">
            <div className="search-card">
              <div className="field-header">
                <div>
                  <span className="field-number">
                    1
                  </span>

                  <div>
                    <h3>
                      Add your inspiration
                    </h3>
                    <p>
                      Upload a garment or outfit
                      you like.
                    </p>
                  </div>
                </div>

                {image && (
                  <button
                    className="text-button"
                    onClick={removeImage}
                  >
                    <X size={15} />
                    Remove
                  </button>
                )}
              </div>

              {!preview ? (
                <div
                  className={`drop-zone ${
                    dragActive
                      ? "drop-active"
                      : ""
                  }`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragActive(true);
                  }}
                  onDragLeave={() =>
                    setDragActive(false)
                  }
                  onDrop={onDrop}
                  onClick={() =>
                    fileInputRef.current?.click()
                  }
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={(e) =>
                      handleFile(
                        e.target.files?.[0]
                      )
                    }
                  />

                  <div className="upload-icon">
                    <ImagePlus size={27} />
                  </div>

                  <h4>
                    Drop your fashion image here
                  </h4>

                  <p>
                    JPG, PNG or WEBP
                  </p>

                  <button className="secondary-button">
                    <Upload size={16} />
                    Choose image
                  </button>
                </div>
              ) : (
                <div className="image-preview-wrap">
                  <img
                    src={preview}
                    alt="Uploaded fashion reference"
                    className="image-preview"
                  />

                  <div className="preview-overlay">
                    <div>
                      <Check size={14} />
                      Image ready
                    </div>
                  </div>
                </div>
              )}

              <div className="divider" />

              <div className="field-header query-header">
                <div>
                  <span className="field-number">
                    2
                  </span>

                  <div>
                    <h3>
                      Tell VYRA what to change
                    </h3>
                    <p>
                      Use natural language.
                    </p>
                  </div>
                </div>
              </div>

              <div className="query-box">
                <Search
                  size={20}
                  className="query-icon"
                />

                <textarea
                  value={query}
                  onChange={(e) =>
                    setQuery(e.target.value)
                  }
                  placeholder='Try "something similar but black under ₹1500"'
                />

                <span className="ai-chip">
                  AI
                </span>
              </div>

              <div className="suggestions">
                <button
                  onClick={() =>
                    setQuery(
                      "something similar but black"
                    )
                  }
                >
                  Similar but black
                </button>

                <button
                  onClick={() =>
                    setQuery(
                      "something similar for women in pink"
                    )
                  }
                >
                  Pink version for women
                </button>

                <button
                  onClick={() =>
                    setQuery(
                      "red tshirt for men under 1000"
                    )
                  }
                >
                  Under ₹1000
                </button>
              </div>

              {error && (
                <div className="error-box">
                  {error}
                </div>
              )}

              <button
                className="search-button"
                onClick={searchProducts}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle
                      size={19}
                      className="spin"
                    />
                    VYRA is reasoning...
                  </>
                ) : (
                  <>
                    Search with VYRA
                    <ArrowRight size={19} />
                  </>
                )}
              </button>

              <p className="privacy-note">
                Your uploaded image is used only
                for this search and is deleted
                after processing.
              </p>
            </div>

            <div className="intelligence-card">
              <div className="intelligence-top">
                <div className="orb">
                  <BrainCircuit size={24} />
                </div>

                <div>
                  <span className="section-kicker">
                    VYRA INTELLIGENCE
                  </span>

                  <h3>
                    How your request is understood
                  </h3>
                </div>
              </div>

              {!response ? (
                <div className="empty-intelligence">
                  <div className="processing-line">
                    <div className="tiny-node" />
                    Image understanding
                  </div>

                  <div className="connector-line" />

                  <div className="processing-line">
                    <div className="tiny-node" />
                    Text intent parsing
                  </div>

                  <div className="connector-line" />

                  <div className="processing-line">
                    <div className="tiny-node" />
                    Constraint validation
                  </div>

                  <div className="connector-line" />

                  <div className="processing-line">
                    <div className="tiny-node" />
                    Multimodal ranking
                  </div>

                  <p>
                    Search to see how VYRA combines
                    your image and language into one
                    structured shopping intent.
                  </p>
                </div>
              ) : (
                <div className="understanding">
                  <div className="understanding-block">
                    <span className="mini-label">
                      TEXT UNDERSTANDING
                    </span>

                    <div className="intent-list">
                      {Object.entries(
                        response.text_intent || {}
                      )
                        .filter(
                          ([, value]) =>
                            value !== null &&
                            (!Array.isArray(value) ||
                              value.length > 0)
                        )
                        .map(([key, value]) => (
                          <div
                            key={key}
                            className="intent-row"
                          >
                            <span>
                              {key.replaceAll(
                                "_",
                                " "
                              )}
                            </span>

                            <strong>
                              {Array.isArray(value)
                                ? value.join(", ")
                                : value}
                            </strong>
                          </div>
                        ))}
                    </div>
                  </div>

                  <div className="understanding-block">
                    <span className="mini-label">
                      IMAGE INFERENCE
                    </span>

                    {Object.entries(
                      response.image_inferred || {}
                    ).map(([key, data]) => (
                      <div
                        className="confidence-row"
                        key={key}
                      >
                        <div>
                          <span>
                            {key}
                          </span>

                          <strong>
                            {data.value}
                          </strong>
                        </div>

                        <div className="confidence">
                          {Math.round(
                            data.confidence * 100
                          )}
                          %
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="understanding-block final-block">
                    <span className="mini-label">
                      FINAL CONSTRAINTS
                    </span>

                    <div className="constraint-pills">
                      {constraints.map(
                        ({ label, value }) => (
                          <span
                            key={`${label}-${value}`}
                          >
                            <Check size={13} />
                            {label}: {value}
                          </span>
                        )
                      )}
                    </div>
                  </div>

                  <div className="safety-note">
                    <ShieldCheck size={18} />
                    <div>
                      <strong>
                        Constraint-safe
                      </strong>
                      <span>
                        Ranking happens only after
                        mandatory requirements are
                        enforced.
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="results-section">
          <div className="results-header">
            <div>
              <span className="section-kicker">
                CURATED FOR YOU
              </span>

              <h2>
                {response
                  ? `${response.result_count} matching ${
                      response.result_count === 1
                        ? "product"
                        : "products"
                    }`
                  : "Your matches will appear here"}
              </h2>

              <p>
                Ranked using semantic relevance,
                visual similarity and verified
                constraints.
              </p>
            </div>

            {response && (
              <div className="result-meta">
                <ShieldCheck size={17} />
                Constraints verified
              </div>
            )}
          </div>

          {!response ? (
            <div className="results-empty">
              <div className="empty-icon">
                <Sparkles size={26} />
              </div>

              <h3>
                Fashion discovery,
                intelligently constrained.
              </h3>

              <p>
                Add a reference image and describe
                what you want. VYRA will do the
                interpretation, validation and
                ranking.
              </p>
            </div>
          ) : response.results.length === 0 ? (
            <div className="results-empty">
              <h3>
                No exact match found
              </h3>

              <p>
                Try relaxing one of your constraints
                while keeping the same inspiration
                image.
              </p>
            </div>
          ) : (
            <div className="product-grid">
              {response.results.map(
                (product, index) => (
                  <article
                    className="product-card"
                    key={product.product_id}
                  >
                    <div className="product-image-wrap">
                      <img
                        src={`${API_BASE}${product.image_url}`}
                        alt={
                          product.product_name
                        }
                      />

                      <span className="rank-badge">
                        #{index + 1}
                      </span>

                      <span className="verified-badge">
                        <ShieldCheck
                          size={13}
                        />
                        Verified match
                      </span>
                    </div>

                    <div className="product-body">
                      <div className="product-brand">
                        {product.brand || "VYRA"}
                      </div>

                      <h3>
                        {product.product_name}
                      </h3>

                      <div className="product-price">
                        ₹
                        {Number(
                          product.price
                        ).toLocaleString(
                          "en-IN"
                        )}
                      </div>

                      <div className="product-tags">
                        {product.category && (
                          <span>
                            {product.category}
                          </span>
                        )}

                        {product.colour_normalized && (
                          <span>
                            {
                              product.colour_normalized
                            }
                          </span>
                        )}

                        {product.gender && (
                          <span>
                            {product.gender}
                          </span>
                        )}
                      </div>

                      <div className="score-area">
                        <div className="score-row">
                          <span>
                            Visual similarity
                          </span>
                          <strong>
                            {Math.round(
                              product.visual_score *
                                100
                            )}
                            %
                          </strong>
                        </div>

                        <div className="score-track">
                          <div
                            className="score-fill"
                            style={{
                              width: `${Math.min(
                                100,
                                Math.max(
                                  0,
                                  product.visual_score *
                                    100
                                )
                              )}%`,
                            }}
                          />
                        </div>

                        <div className="score-row semantic-row">
                          <span>
                            Semantic relevance
                          </span>
                          <strong>
                            {Math.round(
                              product.semantic_score *
                                100
                            )}
                            %
                          </strong>
                        </div>
                      </div>

                      <div className="why-match">
                        <Check size={15} />

                        <span>
                          Matches all mandatory
                          constraints
                        </span>
                      </div>

                      <button className="view-button">
                        View recommendation
                        <ChevronRight
                          size={16}
                        />
                      </button>
                    </div>
                  </article>
                )
              )}
            </div>
          )}
        </section>

        <section className="how-section">
          <div className="how-heading">
            <span className="section-kicker">
              BUILT FOR RELIABLE DISCOVERY
            </span>

            <h2>
              Relevance is useful.
              Correctness is mandatory.
            </h2>
          </div>

          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <BrainCircuit size={21} />
              </div>
              <h3>
                Understand
              </h3>
              <p>
                MiniLM and CLIP interpret language
                and visual context independently.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <ShieldCheck size={21} />
              </div>
              <h3>
                Validate
              </h3>
              <p>
                Hard constraints determine whether
                a recommendation is allowed.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Sparkles size={21} />
              </div>
              <h3>
                Rank
              </h3>
              <p>
                Valid candidates are ranked using
                semantic and visual similarity.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-inner">
          <div className="brand footer-brand">
            <div className="brand-mark">
              V
            </div>

            <div>
              <div className="brand-name">
                VYRA
              </div>
              <div className="brand-sub">
                Intelligent Fashion Search
              </div>
            </div>
          </div>

          <p>
            Multimodal, explainable and
            constraint-safe fashion discovery.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;