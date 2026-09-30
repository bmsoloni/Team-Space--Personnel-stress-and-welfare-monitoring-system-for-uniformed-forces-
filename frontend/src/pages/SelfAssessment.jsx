import { useEffect, useState } from "react";
import { getQuestionsApi, submitWellnessApi } from "../api/wellnessApi";
import { useSelector } from "react-redux";
import toast from "react-hot-toast";
import LoadingSpinner from "../components/common/LoadingSpinner";

export default function SelfAssessment() {
  const { user } = useSelector(s => s.auth);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [consent, setConsent] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => { getQuestionsApi().then(r => { setQuestions(r.data.questions); setLoading(false); }); }, []);

  const handleSubmit = async () => {
    if (!consent) { toast.error("Please provide consent before submitting"); return; }
    toast.loading("Submitting...", { id: "ws" });
    try {
      await submitWellnessApi({ personnel_id: user?.personnel_id, consent_given: true,
        mood_score: answers[1]||5, sleep_quality: answers[2]||5, energy_level: answers[3]||5,
        stress_level: answers[4]||5, social_support: answers[5]||5, responses: answers });
      setSubmitted(true); toast.success("Wellness assessment submitted", { id: "ws" });
    } catch { toast.error("Submission failed", { id: "ws" }); }
  };

  if (loading) return <LoadingSpinner />;
  if (submitted) return (
    <div style={{ display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",minHeight:"50vh",gap:"16px" }}>
      <div style={{ fontSize:"64px" }}>✅</div>
      <h2>Thank You!</h2>
      <p style={{ color:"var(--text-secondary)",textAlign:"center",maxWidth:"400px" }}>Your wellness assessment has been submitted confidentially. This information will only be used to provide you welfare support.</p>
    </div>
  );

  return (
    <div>
      <div className="page-header"><div><h1>Wellness Check-In</h1><div className="breadcrumb">Voluntary and confidential — used only for your welfare support</div></div></div>
      <div style={{ maxWidth:"680px",margin:"0 auto" }}>
        <div className="card" style={{ marginBottom:"20px",background:"rgba(59,130,246,0.05)",border:"1px solid rgba(59,130,246,0.15)" }}>
          <p style={{ fontSize:"13px",color:"var(--text-secondary)",lineHeight:"1.7" }}>🔒 This assessment is <strong>completely voluntary and confidential</strong>. Your responses will only be used by your welfare officer to provide you support. This data will never be used for performance evaluation or disciplinary action.</p>
        </div>
        {questions.map(q => (
          <div key={q.id} className="card" style={{ marginBottom:"16px" }}>
            <div style={{ fontSize:"14px",fontWeight:"500",marginBottom:"16px" }}>{q.id}. {q.text}</div>
            {q.type === "scale" && (
              <div>
                <input type="range" min={q.min} max={q.max} value={answers[q.id]||5} onChange={e => setAnswers(a => ({...a, [q.id]: parseInt(e.target.value)}))} style={{ width:"100%",accentColor:"var(--accent-blue)" }} />
                <div style={{ display:"flex",justifyContent:"space-between",fontSize:"12px",color:"var(--text-muted)",marginTop:"4px" }}>
                  <span>{q.min} (Low)</span><span style={{ fontWeight:"700",color:"var(--accent-blue)",fontSize:"16px" }}>{answers[q.id]||5}</span><span>{q.max} (High)</span>
                </div>
              </div>
            )}
            {q.type === "yesno" && (
              <div style={{ display:"flex",gap:"12px" }}>
                {["Yes","No"].map(opt => (
                  <label key={opt} style={{ display:"flex",alignItems:"center",gap:"8px",cursor:"pointer",padding:"10px 20px",borderRadius:"8px",border:`1px solid ${answers[q.id]===opt?"var(--accent-blue)":"var(--border)"}`,background:answers[q.id]===opt?"rgba(59,130,246,0.1)":"transparent",transition:"var(--transition)" }}>
                    <input type="radio" name={`q${q.id}`} value={opt} checked={answers[q.id]===opt} onChange={() => setAnswers(a => ({...a, [q.id]:opt}))} style={{ display:"none" }} />
                    <span style={{ fontWeight:"600",color:answers[q.id]===opt?"var(--accent-blue)":"var(--text-secondary)" }}>{opt}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        ))}
        <div className="card" style={{ marginBottom:"16px" }}>
          <label style={{ display:"flex",alignItems:"flex-start",gap:"12px",cursor:"pointer" }}>
            <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} style={{ marginTop:"2px",width:"16px",height:"16px",accentColor:"var(--accent-blue)" }} />
            <span style={{ fontSize:"13px",color:"var(--text-secondary)",lineHeight:"1.6" }}>I voluntarily consent to submitting this wellness assessment. I understand that my responses will be kept confidential and used solely for welfare support purposes by authorized welfare officers.</span>
          </label>
        </div>
        <button className="btn btn-primary w-full" style={{ justifyContent:"center",padding:"14px" }} onClick={handleSubmit} disabled={!consent}>
          Submit Wellness Assessment
        </button>
      </div>
    </div>
  );
}
