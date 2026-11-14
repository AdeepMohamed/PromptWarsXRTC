import React, { useEffect, useState } from "react";
import { FolderGit2, Plus, Code2, CheckCircle2, ShieldCheck, BrainCircuit, ExternalLink } from "lucide-react";
import api from "../lib/api";

export function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Form modal
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [techInput, setTechInput] = useState("React, Node.js, PostgreSQL, Tailwind CSS");
  const [githubUrl, setGithubUrl] = useState("https://github.com/alexmorgan/ecommerce-platform");
  const [outcomes, setOutcomes] = useState("Built full stack shop with JWT auth, stripe payment integration, and relational order management.");
  const [submitting, setSubmitting] = useState(false);

  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data.projects || []);
    } catch (err) {
      console.error("Failed to load projects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const techList = techInput.split(",").map((t) => t.trim()).filter(Boolean);
      await api.post("/projects/submit", {
        title,
        description,
        technologies: techList,
        github_url: githubUrl,
        outcomes,
      });
      setShowModal(false);
      setTitle("");
      setDescription("");
      await fetchProjects();
    } catch (err) {
      console.error("Failed to submit project:", err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Loading Portfolio Project Records...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>Demonstrated Practical Evidence</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Project-Based Skill Verification</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Submit production codebases and repository outcomes. AI agents inspect evidence to upgrade claimed skills into demonstrated competencies.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-600/20 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Submit Portfolio Project
        </button>
      </div>

      {/* Projects List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {projects.length === 0 ? (
          <div className="col-span-2 p-12 rounded-3xl bg-white border border-slate-200 text-center text-xs text-slate-500">
            No projects submitted yet. Submit a GitHub project to prove demonstrated competency!
          </div>
        ) : (
          projects.map((p) => (
            <div key={p.id} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-base font-bold text-slate-900">{p.title}</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase bg-emerald-100 text-emerald-800 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Demonstrated Evidence
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-4">{p.description}</p>

                {/* Tech Pills */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {(p.technologies || []).map((t: string) => (
                    <span key={t} className="text-[11px] px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium">
                      {t}
                    </span>
                  ))}
                </div>

                {/* Outcomes */}
                {p.outcomes && (
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700 mb-4">
                    <strong className="block text-slate-900 mb-0.5">Measurable Outcomes:</strong>
                    <span>{p.outcomes}</span>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                {p.github_url ? (
                  <a
                    href={p.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-slate-700 hover:text-slate-900 font-semibold"
                  >
                    <Code2 className="w-4 h-4" /> View Source Code <ExternalLink className="w-3 h-3 text-slate-400" />
                  </a>
                ) : (
                  <span></span>
                )}
                <span className="text-[11px] text-slate-400">
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Submission Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Submit Project for Verification</h3>
            <p className="text-xs text-slate-500 mb-4">Provide project details and link real code repository evidence.</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Project Title
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="E-Commerce REST API & React Storefront"
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Architectural Description
                </label>
                <textarea
                  rows={2}
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Explain the architectural pattern, data model, and systems integration."
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Technologies Used (Comma-separated)
                </label>
                <input
                  type="text"
                  required
                  value={techInput}
                  onChange={(e) => setTechInput(e.target.value)}
                  placeholder="React, TypeScript, Node.js, PostgreSQL"
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  GitHub Repository URL
                </label>
                <input
                  type="url"
                  required
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username/project"
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Deliverables & Measurable Outcomes
                </label>
                <textarea
                  rows={2}
                  value={outcomes}
                  onChange={(e) => setOutcomes(e.target.value)}
                  placeholder="Implemented unit tests, CI/CD pipeline, and deployed on Render with PostgreSQL."
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-500 hover:text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-md disabled:opacity-50"
                >
                  {submitting ? "Analyzing Project..." : "Submit Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
