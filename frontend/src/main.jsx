import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Database,
  Eye,
  FileSearch,
  ImagePlus,
  Layers3,
  MessageSquareText,
  Microscope,
  PhoneCall,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Stethoscope,
  Upload,
  X,
} from "lucide-react";
import "./styles.css";
import heroImage from "./assets/ophthalmology-hero.png";
import { isSupabaseConfigured, supabase } from "./lib/supabaseClient";

const urgentText =
  "Seek immediate care for sudden vision loss, severe pain, injury, chemical exposure, flashes, floaters, or a curtain over vision.";

const quickPrompts = [
  "What should I do for blurry vision and eye pain?",
  "Explain glaucoma symptoms in simple language.",
  "When should floaters be treated as urgent?",
];

const welcomeMessage = {
  role: "assistant",
  text: "Ask about eye symptoms, conditions, or care. You may upload scanned eye image for screening support. This tool is informational and cannot confirm a diagnosis.",
  time: "OcuCare Assistant",
};

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

function Button({ className, variant = "primary", children, ...props }) {
  return (
    <a
      className={cn(
        "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-blue-200",
        variant === "primary" && "bg-blue-700 text-white shadow-lg shadow-blue-900/20 hover:bg-blue-800",
        variant === "secondary" && "border border-slate-300 bg-white text-slate-800 shadow-sm hover:border-blue-300 hover:text-blue-800",
        variant === "ghost" && "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
        className
      )}
      {...props}
    >
      {children}
    </a>
  );
}

function Card({ className, children }) {
  return (
    <div className={cn("rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-950/5", className)}>
      {children}
    </div>
  );
}

function Badge({ className, children, tone = "teal" }) {
  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide",
        tone === "teal" && "bg-teal-50 text-teal-800 ring-1 ring-teal-200",
        tone === "blue" && "bg-blue-50 text-blue-800 ring-1 ring-blue-200",
        tone === "red" && "bg-red-50 text-red-800 ring-1 ring-red-200",
        tone === "amber" && "bg-amber-50 text-amber-800 ring-1 ring-amber-200",
        className
      )}
    >
      {children}
    </span>
  );
}

function Brand() {
  return (
    <a className="flex items-center gap-3" href="/" aria-label="OcuCare home">
      <span className="relative grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-teal-700 via-teal-600 to-blue-700 text-white shadow-xl shadow-teal-900/20 ring-1 ring-white/60">
        <span className="absolute inset-1.5 rounded-xl border border-white/25" />
        <Eye size={24} strokeWidth={2.4} />
        <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-emerald-300 ring-2 ring-teal-700" />
      </span>
      <span className="leading-tight">
        <strong className="block text-lg font-black tracking-tight text-slate-950">OcuCare</strong>
        <small className="block text-xs font-semibold text-slate-500">Ophthalmology AI support</small>
      </span>
    </a>
  );
}

function Header({ assistant = false }) {
  const nav = assistant
    ? [["Home", "/"], ["Resources", "/#resources"], ["Contact", "/#contact"]]
    : [["Platform", "#platform"], ["Workflow", "#workflow"], ["Evaluation", "#evaluation"], ["Resources", "#resources"], ["Contact", "#contact"]];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 px-5 py-3 backdrop-blur-xl lg:px-10">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-5">
        <Brand />
        <nav className="hidden items-center gap-1 rounded-full border border-slate-200 bg-slate-50 p-1 md:flex">
          {nav.map(([label, href]) => (
            <a key={label} href={href} className="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-slate-950 hover:shadow-sm">
              {label}
            </a>
          ))}
        </nav>
        <Button href="/bot" className="shrink-0">
          <MessageSquareText size={17} />
          Open Assistant
        </Button>
      </div>
    </header>
  );
}

function LandingPage() {
  const workflow = [
    ["01", MessageSquareText, "Source-grounded triage", "Text questions are answered as educational guidance with evidence context when retrieval is available."],
    ["02", ImagePlus, "Fundus image screening", "Image predictions are presented as screening support for selected trained disease classes."],
    ["03", Layers3, "Multimodal consistency", "Image evidence and symptom descriptions are compared to expose disagreement."],
    ["04", ShieldAlert, "Safety escalation", "Urgent symptoms override routine flow and push the user toward professional care."],
  ];

  const resources = [
    ["Urgent care", "When eye symptoms need immediate attention", urgentText],
    ["Evidence", "How source-grounded answers help reviewers", "Retrieved context makes the answer traceable and easier to defend during evaluation."],
    ["Limitations", "Why class-limited models must stay cautious", "Unsupported diseases and low-confidence outputs should be described as uncertain."],
  ];

  return (
    <div className="min-h-screen bg-[#eef3f8] text-slate-900">
      <Header />
      <main>
        <section id="platform" className="clinical-grid relative overflow-hidden px-5 py-12 lg:px-10 lg:py-16">
          <div className="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-[1.02fr_0.98fr]">
            <div>
              <Badge tone="teal"><Sparkles size={14} /> Modern clinical AI prototype</Badge>
              <h1 className="mt-6 max-w-4xl text-5xl font-black leading-tight text-slate-950 lg:text-7xl">
                A clinical-grade eye screening interface for safer AI research.
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
                OcuCare now presents your CNN, multimodal model, and source-grounded chatbot as one
                polished ophthalmology support platform with visible evidence, uncertainty, and escalation.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button href="/bot">Launch assistant <ArrowRight size={18} /></Button>
                <Button href="#evaluation" variant="secondary">View evaluation</Button>
              </div>
              <div className="mt-8 grid max-w-3xl gap-3 sm:grid-cols-3">
                <HeroProof icon={Database} value="RAG" label="Evidence-grounded answers" />
                <HeroProof icon={Microscope} value="CNN" label="Fundus screening support" />
                <HeroProof icon={Layers3} value="Fusion" label="Image-text consistency" />
              </div>
              <div className="mt-8 flex max-w-3xl gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-900 shadow-sm">
                <AlertTriangle className="mt-0.5 shrink-0" size={19} />
                <span>{urgentText}</span>
              </div>
            </div>

            <HeroShowcase />
          </div>
        </section>

        <section className="px-5 pb-12 lg:px-10">
          <div className="mx-auto grid max-w-7xl gap-4 md:grid-cols-4">
            <Capability icon={Database} title="RAG evidence" text="Source context" />
            <Capability icon={Microscope} title="Image model" text="CNN screening" />
            <Capability icon={BrainCircuit} title="Fusion model" text="Image + symptoms" />
            <Capability icon={ShieldAlert} title="Guardrails" text="Urgent escalation" />
          </div>
        </section>

        <Section id="workflow" label="Workflow" title="Built around defensible research behavior, not generic chatbot answers.">
          <div className="mb-5 grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
            <Card className="overflow-hidden p-0">
              <div className="bg-slate-950 p-6 text-white">
                <Badge tone="blue" className="bg-white/10 text-white ring-white/20">Research contribution</Badge>
                <h3 className="mt-4 text-2xl font-black">The value is not another chatbot. It is the safety workflow around the models.</h3>
                <p className="mt-3 text-sm leading-6 text-slate-300">The interface now makes that contribution visible: text-only triage, class-limited imaging, multimodal contradiction checks, and emergency escalation all appear as separate controlled paths.</p>
              </div>
              <div className="grid gap-0 divide-y divide-slate-200 md:grid-cols-3 md:divide-x md:divide-y-0">
                <Contribution label="Without scan" value="Text triage + RAG" />
                <Contribution label="With scan" value="CNN screening" />
                <Contribution label="Contradictory text" value="Conflict detection" />
              </div>
            </Card>
            <Card className="p-6">
              <Badge tone="amber">Presentation angle</Badge>
              <h3 className="mt-4 text-2xl font-black text-slate-950">Answer your lecturers directly</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">The page now shows why OcuCare is different from uploading a PDF to Gemini: it combines controlled retrieval, image evidence, multimodal disagreement handling, and explicit safety boundaries.</p>
              <div className="mt-5 space-y-3">
                <RiskRow label="PDF chatbot problem" value="Handled with RAG evidence" />
                <RiskRow label="No scan available" value="Text-only triage path" />
                <RiskRow label="Fake symptom text" value="Consistency warning" urgent />
              </div>
            </Card>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {workflow.map(([step, Icon, title, text]) => (
              <Card key={title} className="group p-6 transition hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-950/10">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-black text-slate-400">{step}</span>
                  <span className="grid h-11 w-11 place-items-center rounded-2xl bg-teal-50 text-teal-700 ring-1 ring-teal-100">
                    <Icon size={21} />
                  </span>
                </div>
                <h3 className="mt-8 text-lg font-black text-slate-950">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{text}</p>
              </Card>
            ))}
          </div>
        </Section>

        <Section id="evaluation" label="Evaluation" title="Show measured checks as research evidence, not clinical claims." tinted>
          <div className="grid gap-5 md:grid-cols-3">
            <Metric value="10 / 10" label="RAG safety and evidence checks" />
            <Metric value="5 / 5" label="Image-only screening checks" />
            <Metric value="9 / 10" label="Latest visible multimodal safety run" />
          </div>
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            <Info title="What reviewers can inspect" text="Triage framing, retrieved evidence, uncertainty language, image-text disagreement, and urgent symptom escalation." />
            <Info title="What the system does not claim" text="Clinical safety, broad disease coverage, or diagnostic accuracy without ophthalmologist review and external validation." />
          </div>
        </Section>

        <Section id="resources" label="Resources" title="Educational content without invented contacts or unsourced live news.">
          <div className="grid gap-5 md:grid-cols-3">
            {resources.map(([tag, title, text]) => (
              <Card key={title} className="p-6">
                <Badge tone={tag === "Urgent care" ? "red" : "teal"}>{tag}</Badge>
                <h3 className="mt-5 text-xl font-black text-slate-950">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{text}</p>
              </Card>
            ))}
          </div>
        </Section>

        <section id="contact" className="px-5 py-12 lg:px-10">
          <div className="mx-auto flex max-w-7xl flex-col gap-6 rounded-3xl border border-slate-200 bg-slate-950 p-8 text-white shadow-2xl shadow-slate-950/20 md:flex-row md:items-center md:justify-between">
            <div>
              <Badge tone="blue" className="bg-white/10 text-white ring-white/20">Contact and escalation</Badge>
              <h2 className="mt-4 max-w-3xl text-3xl font-black">Use OcuCare as screening support, never as a replacement for professional care.</h2>
              <p className="mt-3 max-w-3xl text-slate-300">For real symptoms, contact a licensed ophthalmologist, eye clinic, hospital eye unit, or local emergency service.</p>
            </div>
            <Button href="/bot" className="bg-white text-slate-950 hover:bg-slate-100">Open Assistant <ChevronRight size={18} /></Button>
          </div>
        </section>
      </main>
      <footer className="border-t border-slate-200 bg-white px-5 py-6 text-sm text-slate-500 lg:px-10">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-3 md:flex-row">
          <p>OcuCare is an educational screening-support research prototype. It is not clinically validated.</p>
          <p>Copyright 2026 OcuCare Research Project</p>
        </div>
      </footer>
    </div>
  );
}

function HeroProof({ icon: Icon, value, label }) {
  return (
    <div className="rounded-2xl border border-white/70 bg-white/80 p-4 shadow-lg shadow-slate-950/5 backdrop-blur">
      <Icon className="text-teal-700" size={19} />
      <strong className="mt-3 block text-lg font-black text-slate-950">{value}</strong>
      <span className="text-sm font-medium text-slate-600">{label}</span>
    </div>
  );
}

function Contribution({ label, value }) {
  return (
    <div className="p-5">
      <span className="text-xs font-black uppercase tracking-wide text-slate-400">{label}</span>
      <strong className="mt-2 block text-base text-slate-950">{value}</strong>
    </div>
  );
}

function HeroShowcase() {
  return (
    <div className="relative lg:-translate-y-16 xl:-translate-y-24 2xl:-translate-y-28">
      <div className="absolute -inset-5 rounded-[2.2rem] bg-gradient-to-br from-blue-200 via-teal-100 to-white blur-2xl" />
      <Card className="glass-panel relative overflow-hidden p-0">
        <div className="relative h-[500px] overflow-hidden rounded-2xl">
          <img className="h-full w-full object-cover" src={heroImage} alt="Ophthalmology clinician reviewing retinal imaging on a diagnostic workstation" />
          <div className="absolute inset-0 bg-gradient-to-tr from-slate-950/70 via-slate-950/15 to-white/10" />
          <div className="absolute left-5 top-5 flex gap-2">
            <Badge tone="blue" className="bg-white/90"><Activity size={14} /> Screening console</Badge>
            <Badge tone="teal" className="bg-white/90"><CheckCircle2 size={14} /> Prototype ready</Badge>
          </div>
          <div className="absolute bottom-5 left-5 right-5 grid gap-4 lg:grid-cols-[1fr_250px]">
            <div className="rounded-3xl border border-white/20 bg-white/90 p-5 shadow-2xl backdrop-blur-xl">
              <span className="text-xs font-black uppercase tracking-wide text-teal-800">Case workflow</span>
              <h2 className="mt-2 text-2xl font-black text-slate-950">Multimodal ophthalmology review</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">Image evidence, symptom text, retrieved context, and urgent symptom checks are presented together.</p>
            </div>
            <div className="rounded-3xl border border-white/20 bg-slate-950/86 p-4 text-white shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="text-xs font-bold uppercase tracking-wide text-slate-300">Safety gate</span>
                <ShieldAlert className="text-red-300" size={18} />
              </div>
              <div className="mt-3 space-y-2">
                <RiskRow label="Evidence" value="Visible" />
                <RiskRow label="Scope" value="Bounded" />
                <RiskRow label="Red flags" value="Escalate" urgent />
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

function RiskRow({ label, value, urgent = false }) {
  return (
    <div className={cn("flex items-center justify-between gap-4 rounded-2xl border p-3 text-sm", urgent ? "border-red-200 bg-red-50 text-slate-950" : "border-slate-200 bg-white text-slate-950")}>
      <span className="font-medium text-slate-500">{label}</span>
      <strong className={urgent ? "text-red-800" : "text-slate-950"}>{value}</strong>
    </div>
  );
}

function Capability({ icon: Icon, title, text }) {
  return (
    <Card className="flex items-center gap-4 p-4">
      <span className="grid h-12 w-12 place-items-center rounded-2xl bg-white text-teal-700 ring-1 ring-slate-200">
        <Icon size={21} />
      </span>
      <span>
        <strong className="block text-sm text-slate-950">{title}</strong>
        <small className="text-sm text-slate-500">{text}</small>
      </span>
    </Card>
  );
}

function Section({ id, label, title, children, tinted = false }) {
  return (
    <section id={id} className={cn("px-5 py-16 lg:px-10", tinted && "bg-white/60")}>
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 max-w-3xl">
          <Badge tone="teal">{label}</Badge>
          <h2 className="mt-4 text-3xl font-black leading-tight text-slate-950 lg:text-4xl">{title}</h2>
        </div>
        {children}
      </div>
    </section>
  );
}

function Metric({ value, label }) {
  return (
    <Card className="p-6">
      <strong className="block text-4xl font-black text-blue-800">{value}</strong>
      <span className="mt-3 block text-sm font-medium text-slate-600">{label}</span>
    </Card>
  );
}

function Info({ title, text }) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-black text-slate-950">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-600">{text}</p>
    </Card>
  );
}

function AssistantPage() {
  const [messages, setMessages] = useState([welcomeMessage]);
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [authSession, setAuthSession] = useState(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authNotice, setAuthNotice] = useState("");
  const [chatSessions, setChatSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [patientSummary, setPatientSummary] = useState(null);
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryNotice, setSummaryNotice] = useState("");
  const fileInputRef = useRef(null);
  const activeMode = file && text.trim() ? "Image + symptoms" : file ? "Image-only" : "Text-only";
  const user = authSession?.user || null;

  function resetFile() {
    setFile(null);
    setPreview("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  useEffect(() => {
    if (!isSupabaseConfigured) return;

    supabase.auth.getSession().then(({ data }) => {
      setAuthSession(data.session || null);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthSession(session || null);
      if (!session) {
        setChatSessions([]);
        setActiveSessionId(null);
        setPatientSummary(null);
        setSummaryOpen(false);
        setMessages([welcomeMessage]);
      }
    });

    return () => listener.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    loadChatSessions();
    loadPatientSummary();
  }, [user?.id]);

  async function signIn(event) {
    event.preventDefault();
    if (!isSupabaseConfigured || !authEmail.trim()) return;

    const { error } = await supabase.auth.signInWithOtp({
      email: authEmail.trim(),
      options: {
        emailRedirectTo: window.location.origin + "/bot",
      },
    });

    setAuthNotice(error ? error.message : "Check your email for the login link.");
  }

  async function signOut() {
    if (!isSupabaseConfigured) return;
    await supabase.auth.signOut();
    setAuthNotice("");
    setSummaryNotice("");
  }

  async function loadChatSessions() {
    if (!user) return;
    setHistoryLoading(true);
    const { data, error } = await supabase
      .from("chat_sessions")
      .select("id,title,mode,created_at,updated_at")
      .order("updated_at", { ascending: false });
    if (!error) setChatSessions(data || []);
    setHistoryLoading(false);
  }

  async function loadPatientSummary() {
    if (!user) return;
    const { data, error } = await supabase
      .from("patient_summaries")
      .select("*")
      .eq("user_id", user.id)
      .maybeSingle();
    if (!error) setPatientSummary(data || null);
  }

  async function ensureChatSession(firstText = "") {
    if (!user) return null;
    if (activeSessionId) return activeSessionId;

    const title = titleFromMessage(firstText);
    const { data, error } = await supabase
      .from("chat_sessions")
      .insert({
        user_id: user.id,
        title,
        mode: activeMode.toLowerCase(),
      })
      .select("id,title,mode,created_at,updated_at")
      .single();

    if (error) {
      setAuthNotice(error.message);
      return null;
    }

    setActiveSessionId(data.id);
    setChatSessions(prev => [data, ...prev]);
    return data.id;
  }

  async function saveChatMessage(sessionId, message, clinicalMetadata = {}) {
    if (!user || !sessionId) return false;
    const { error } = await supabase.from("chat_messages").insert({
      session_id: sessionId,
      user_id: user.id,
      role: message.role,
      content: message.text || "",
      image_name: message.imageName || null,
      image_present: Boolean(message.image),
      metadata: {
        client_time: message.time,
        mode: clinicalMetadata.mode || activeMode,
        ...clinicalMetadata,
      },
    });
    if (error) {
      setAuthNotice(error.message);
      setSummaryNotice(`Chat save failed: ${error.message}`);
      return false;
    }
    await supabase
      .from("chat_sessions")
      .update({ mode: activeMode.toLowerCase() })
      .eq("id", sessionId);
    loadChatSessions();
    return true;
  }

  async function loadSessionMessages(sessionId) {
    if (!user) return;
    setHistoryLoading(true);
    const { data, error } = await supabase
      .from("chat_messages")
      .select("role,content,image_name,image_present,created_at,metadata")
      .eq("session_id", sessionId)
      .order("created_at", { ascending: true });

    if (!error) {
      setActiveSessionId(sessionId);
      setMessages([
        welcomeMessage,
        ...(data || []).map(row => ({
          role: row.role,
          text: row.content,
          time: row.metadata?.client_time || formatStoredTime(row.created_at),
          image: "",
          imageName: row.image_name,
          image_present: row.image_present,
        })),
      ]);
      loadPatientSummary();
    }
    setHistoryLoading(false);
  }

  async function autoGeneratePatientSummary() {
    if (!user || summaryLoading) return;
    setSummaryLoading(true);
    setSummaryNotice("Updating eye-health summary automatically...");

    try {
      const { data, error } = await supabase
        .from("chat_messages")
        .select("role,content,image_present,created_at,metadata")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })
        .limit(300);
      if (error) throw error;

      const rows = (data || [])
        .reverse()
        .filter(isSummaryEligibleRow)
        .slice(-120);
      if (rows.length === 0) {
        setSummaryNotice("No clinically important saved information is available for a summary yet.");
        return;
      }

      let rawSummary;
      const summaryController = new AbortController();
      const summaryTimeout = window.setTimeout(() => summaryController.abort(), 25000);
      try {
        const response = await fetch("/summary", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: rows.map(toSummaryMessage),
          }),
          signal: summaryController.signal,
        });
        if (!response.ok) throw new Error("Summary generation failed");
        rawSummary = await response.json();
      } catch {
        rawSummary = { generation_status: "fallback" };
      } finally {
        window.clearTimeout(summaryTimeout);
      }
      const summary = enrichFallbackSummary(rawSummary, rows);

      const saved = {
        user_id: user.id,
        summary_text: summary.summary_text || "",
        symptoms: Array.isArray(summary.symptoms) ? summary.symptoms : [],
        topics: Array.isArray(summary.topics) ? summary.topics : [],
        red_flags: Array.isArray(summary.red_flags) ? summary.red_flags : [],
        image_history: Array.isArray(summary.image_history) ? summary.image_history : [],
        recommended_next_steps: Array.isArray(summary.recommended_next_steps) ? summary.recommended_next_steps : [],
        safety_note: summary.safety_note || "This is not a diagnosis. It summarizes user-reported information and AI screening-support outputs.",
        last_generated_at: new Date().toISOString(),
      };

      const { data: upserted, error: upsertError } = await supabase
        .from("patient_summaries")
        .upsert(saved, { onConflict: "user_id" })
        .select("*")
        .single();
      if (upsertError) throw upsertError;

      setPatientSummary({ ...upserted, generation_status: summary.generation_status || "generated" });
      setSummaryNotice(
        summary.generation_status === "fallback"
          ? "Gemini summary generation was unavailable. Showing a local safety summary; use refresh to try again."
          : "Eye-health summary updated from saved chats."
      );
    } catch (error) {
      setSummaryNotice(error.message || "Could not update summary.");
    } finally {
      setSummaryLoading(false);
    }
  }

  async function openSummaryModal() {
    setSummaryOpen(true);
    if (user && !summaryLoading) {
      await autoGeneratePatientSummary();
    }
  }

  function startNewChat() {
    setActiveSessionId(null);
    setMessages([welcomeMessage]);
    resetFile();
    setText("");
  }

  function onFileChange(event) {
    const selected = event.target.files?.[0];
    if (!selected) return resetFile();
    setFile(selected);
    const reader = new FileReader();
    reader.onload = event => setPreview(String(event.target.result || ""));
    reader.readAsDataURL(selected);
  }

  async function submit(event) {
    event.preventDefault();
    const cleanText = text.trim();
    if ((!cleanText && !file) || busy) return;

    const formData = new FormData();
    if (cleanText) formData.append("msg", cleanText);
    if (file) formData.append("image", file);

    const hadImage = Boolean(file);
    const submittedMode = activeMode;
    const userMessage = {
      role: "user",
      text: cleanText,
      image: preview,
      imageName: file?.name || null,
      time: formatTime(),
    };

    setMessages(prev => [...prev, userMessage]);
    setText("");
    resetFile();
    setBusy(true);

    try {
      const response = await fetch("/get", { method: "POST", body: formData });
      if (!response.ok) throw new Error("Request failed");
      const data = await response.text();
      const assistantMessage = { role: "assistant", text: data, time: `${formatTime()} - OcuCare` };
      setMessages(prev => [...prev, assistantMessage]);
      const outcome = classifyChatOutcome(data, { hadImage, userText: cleanText, mode: submittedMode });

      if (outcome.image_rejected) {
        setSummaryNotice("Rejected image interactions are not saved or included in the patient summary.");
        return;
      }

      const sessionId = user ? await ensureChatSession(cleanText || "Image screening chat") : null;
      const userSaved = await saveChatMessage(sessionId, userMessage, {
        ...outcome,
        role_context: "patient_input",
        include_in_summary: outcome.include_in_summary || isClinicallyImportantText(cleanText),
      });
      const assistantSaved = await saveChatMessage(sessionId, assistantMessage, {
        ...outcome,
        role_context: "assistant_result",
      });
      if (userSaved && assistantSaved && outcome.include_in_summary) await autoGeneratePatientSummary();
    } catch {
      const errorMessage = { role: "assistant", text: "We could not process your request. Please try again.", time: formatTime(), error: true };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <Header assistant />
      <main className="grid h-[calc(100vh-73px)] gap-4 p-4 lg:grid-cols-[340px_minmax(0,1fr)] lg:p-5">
        <aside className="space-y-4 overflow-y-auto">
          <AuthPanel
            user={user}
            authEmail={authEmail}
            setAuthEmail={setAuthEmail}
            authNotice={authNotice}
            signIn={signIn}
            signOut={signOut}
          />
          {user && (
            <Card className="p-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-lg font-black text-slate-950">Previous chats</h2>
                <button className="rounded-xl border border-slate-200 px-3 py-1.5 text-xs font-black text-blue-800 hover:bg-blue-50" type="button" onClick={startNewChat}>
                  New
                </button>
              </div>
              <div className="mt-4 space-y-2">
                {historyLoading && <p className="text-sm text-slate-500">Loading history...</p>}
                {!historyLoading && chatSessions.length === 0 && <p className="text-sm text-slate-500">No saved chats yet.</p>}
                {chatSessions.map(session => (
                  <button
                    className={cn(
                      "w-full rounded-2xl border p-3 text-left transition hover:border-blue-300 hover:bg-blue-50",
                      activeSessionId === session.id ? "border-blue-300 bg-blue-50" : "border-slate-200 bg-white"
                    )}
                    key={session.id}
                    type="button"
                    onClick={() => loadSessionMessages(session.id)}
                  >
                    <strong className="block truncate text-sm text-slate-950">{session.title}</strong>
                    <span className="text-xs text-slate-500">{formatStoredTime(session.updated_at)}</span>
                  </button>
                ))}
              </div>
            </Card>
          )}
          <Card className="p-5">
            <h2 className="text-lg font-black text-slate-950">Suggested prompts</h2>
            <div className="mt-4 space-y-2">
              {quickPrompts.map(prompt => (
                <button key={prompt} className="w-full rounded-2xl border border-slate-200 bg-white p-3 text-left text-sm font-medium text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-900" type="button" onClick={() => setText(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          </Card>
          <Card className="p-5">
            <h2 className="text-lg font-black text-slate-950">Response review</h2>
            <ReviewItem icon={FileSearch} label="Patient-facing report view" />
            <ReviewItem icon={AlertTriangle} label="Red flags separated" />
            <ReviewItem icon={Stethoscope} label="Next step clearly stated" />
          </Card>
          <Card className="border-amber-200 bg-amber-50 p-5">
            <h2 className="text-lg font-black text-amber-950">Research boundary</h2>
            <p className="mt-2 text-sm leading-6 text-amber-900">Outputs are not medical diagnosis. Keep limitations visible in demos and final presentation.</p>
          </Card>
        </aside>

        <section className="flex min-h-0 flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-950/10">
          <div className="flex items-start justify-between gap-5 border-b border-slate-200 px-5 py-4">
            <div>
              <Badge tone="blue"><Microscope size={14} /> OcuCare assistant</Badge>
              <h2 className="mt-2 text-2xl font-black text-slate-950">Patient guidance chat</h2>
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2">
              {user && (
                <button
                  className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 text-sm font-black text-blue-800 hover:bg-blue-100"
                  type="button"
                  onClick={openSummaryModal}
                >
                  <Activity size={16} />
                  Eye Health Summary
                </button>
              )}
              <Badge tone="teal">Research prototype</Badge>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto bg-slate-50 p-5">
            {messages.map((message, index) => <ChatMessage key={`${message.role}-${index}`} message={message} />)}
            {busy && <TypingIndicator />}
          </div>

          {preview && (
            <div className="flex items-center gap-3 border-t border-slate-200 bg-white px-5 py-3">
              <img className="h-14 w-14 rounded-2xl object-cover ring-1 ring-slate-200" src={preview} alt="Selected eye upload preview" />
              <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-600">{file?.name || "Image selected"}</span>
              <button className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-slate-200 px-3 text-sm font-semibold text-red-700 hover:bg-red-50" type="button" onClick={resetFile}>
                <X size={16} /> Remove
              </button>
            </div>
          )}

          <form className="border-t border-slate-200 bg-white p-4" onSubmit={submit}>
            <p className="mb-3 text-sm font-medium text-red-800">{urgentText}</p>
            <div className="flex gap-3">
              <label className="relative grid h-12 w-12 shrink-0 cursor-pointer place-items-center rounded-2xl border border-slate-200 bg-white text-blue-700 transition hover:border-blue-300 hover:bg-blue-50" title="Upload eye image" aria-label="Upload eye image">
                <Upload size={20} />
                <input ref={fileInputRef} className="absolute inset-0 cursor-pointer opacity-0" type="file" accept="image/*" onChange={onFileChange} />
              </label>
              <input className="min-w-0 flex-1 rounded-2xl border border-slate-200 px-4 text-sm outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-100" value={text} onChange={event => setText(event.target.value)} placeholder="Describe symptoms or ask an eye-health question..." />
              <button className="min-h-12 rounded-2xl bg-blue-700 px-5 text-sm font-black text-white shadow-lg shadow-blue-900/20 transition hover:bg-blue-800 disabled:opacity-60" type="submit" disabled={busy}>Send</button>
            </div>
          </form>
        </section>

      </main>
      {summaryOpen && (
        <SummaryModal
          summary={patientSummary}
          summaryLoading={summaryLoading}
          summaryNotice={summaryNotice}
          onRefresh={autoGeneratePatientSummary}
          onClose={() => setSummaryOpen(false)}
        />
      )}
    </div>
  );
}

function SummaryModal({ summary, summaryLoading, summaryNotice, onRefresh, onClose }) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/55 p-4 backdrop-blur-sm">
      <div className="max-h-[88vh] w-full max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 p-6">
          <div>
            <Badge tone="blue"><Activity size={14} /> Automatic patient summary</Badge>
            <h2 className="mt-3 text-2xl font-black text-slate-950">Eye Health Summary</h2>
            <p className="mt-2 text-sm text-slate-600">Generated automatically from saved chats and screening-support outputs.</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
              type="button"
              onClick={onRefresh}
              disabled={summaryLoading}
              aria-label="Regenerate summary from saved chats"
              title="Regenerate summary from saved chats"
            >
              <RefreshCw className={summaryLoading ? "animate-spin" : ""} size={18} />
            </button>
            <button className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50" type="button" onClick={onClose} aria-label="Close summary">
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="max-h-[calc(88vh-128px)] overflow-y-auto p-6">
          {summaryLoading && (
            <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm font-medium text-blue-900">
              Updating the latest summary automatically...
            </div>
          )}
          {!summary && !summaryLoading && (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
              <h3 className="text-lg font-black text-amber-950">No summary yet</h3>
              <p className="mt-2 text-sm leading-6 text-amber-900">OcuCare will generate this automatically from saved logged-in chats. If you already chatted, wait a moment and reopen this panel.</p>
            </div>
          )}
          {summary && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <h3 className="text-lg font-black text-slate-950">Overview</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">{summary.summary_text}</p>
                {summary.last_generated_at && (
                  <p className="mt-3 text-xs font-medium text-slate-500">Last generated: {formatStoredTime(summary.last_generated_at)}</p>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <SummaryList title="Reported Symptoms" items={summary.symptoms} empty="No symptoms identified yet." />
                <SummaryList title="Topics Discussed" items={summary.topics} empty="No topics identified yet." />
                <SummaryList title="Red Flags" items={summary.red_flags} empty="No urgent warning signs found in saved chats." urgent />
                <SummaryList title="Accepted Screening Findings" items={summary.image_history} empty="No accepted image-screening findings yet." />
              </div>
              <SummaryList title="Recommended Next Steps" items={summary.recommended_next_steps} empty="No next steps generated yet." wide />
              <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-900">
                <strong>Safety note: </strong>
                {summary.safety_note || "This is not a diagnosis. It summarizes user-reported information and AI screening-support outputs."}
              </div>
            </div>
          )}
          {summaryNotice && (
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
              {summaryNotice}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SummaryList({ title, items, empty, urgent = false, wide = false }) {
  const list = Array.isArray(items) ? items.filter(Boolean) : [];
  return (
    <div className={cn("rounded-2xl border p-5", urgent ? "border-red-200 bg-red-50" : "border-slate-200 bg-white", wide && "md:col-span-2")}>
      <h3 className={cn("text-base font-black", urgent ? "text-red-950" : "text-slate-950")}>{title}</h3>
      {list.length === 0 ? (
        <p className="mt-2 text-sm leading-6 text-slate-500">{empty}</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {list.map((item, index) => (
            <li className="flex gap-2 text-sm leading-6 text-slate-700" key={`${title}-${index}`}>
              <CheckCircle2 className={urgent ? "mt-1 shrink-0 text-red-700" : "mt-1 shrink-0 text-teal-700"} size={15} />
              <span>{String(item)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AuthPanel({ user, authEmail, setAuthEmail, authNotice, signIn, signOut }) {
  if (!isSupabaseConfigured) {
    return (
      <Card className="border-amber-200 bg-amber-50 p-5">
        <h2 className="text-lg font-black text-amber-950">Login disabled</h2>
        <p className="mt-2 text-sm leading-6 text-amber-900">Add Supabase environment variables and rebuild to enable saved chat history.</p>
      </Card>
    );
  }

  if (user) {
    return (
      <Card className="p-5">
        <Badge tone="teal">Signed in</Badge>
        <h2 className="mt-3 text-lg font-black text-slate-950">Chat history enabled</h2>
        <p className="mt-2 break-all text-sm text-slate-600">{user.email}</p>
        <button className="mt-4 min-h-10 rounded-xl border border-slate-200 px-4 text-sm font-black text-slate-700 hover:bg-slate-50" type="button" onClick={signOut}>
          Sign out
        </button>
      </Card>
    );
  }

  return (
    <Card className="p-5">
      <Badge tone="blue">Optional login</Badge>
      <h2 className="mt-3 text-lg font-black text-slate-950">Save previous chats</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">Continue anonymously, or sign in by email to save and reload chat sessions.</p>
      <form className="mt-4 space-y-3" onSubmit={signIn}>
        <input
          className="h-11 w-full rounded-xl border border-slate-200 px-3 text-sm outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100"
          type="email"
          value={authEmail}
          onChange={event => setAuthEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <button className="min-h-11 w-full rounded-xl bg-slate-950 px-4 text-sm font-black text-white hover:bg-slate-800" type="submit">
          Send login link
        </button>
      </form>
      {authNotice && <p className="mt-3 text-sm text-slate-600">{authNotice}</p>}
    </Card>
  );
}

function ReviewItem({ icon: Icon, label }) {
  return (
    <div className="flex items-center gap-3 border-t border-slate-200 py-3 text-sm font-medium text-slate-600 first:border-t-0">
      <Icon className="text-teal-700" size={18} />
      {label}
    </div>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("mb-5 flex gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-teal-50 text-xs font-black text-teal-800 ring-1 ring-teal-100">OC</div>}
      <div className={cn("max-w-[78%] rounded-3xl border p-4 shadow-sm", isUser ? "border-blue-700 bg-blue-700 text-white" : "border-slate-200 bg-white", message.error && "border-red-200 bg-red-50")}>
        {message.image && <img className="mb-3 max-h-48 max-w-64 rounded-2xl object-cover ring-1 ring-white/40" src={message.image} alt="Uploaded eye image" />}
        {isUser ? <p className="whitespace-pre-wrap text-sm leading-6">{message.text}</p> : <StructuredResponse text={message.text} />}
        <time className={cn("mt-3 block text-xs", isUser ? "text-blue-100" : "text-slate-400")}>{message.time}</time>
      </div>
      {isUser && <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-blue-50 text-xs font-black text-blue-800 ring-1 ring-blue-100">You</div>}
    </div>
  );
}

function StructuredResponse({ text }) {
  const parsedSections = dedupeSections(parseResponse(text));
  const visibleSections = parsedSections.filter(section => !["evidence", "hidden"].includes(section.kind));
  const sections = visibleSections.length > 0
    ? visibleSections
    : [{ title: "", body: String(text || "").trim(), kind: "default" }];
  return (
    <div className="space-y-4">
      {sections.map((section, index) => (
        <section className={sectionClass(section.kind)} key={`${section.title}-${index}`}>
          {section.title && <h3 className="mb-3 text-[13px] font-black uppercase tracking-wide text-slate-900">{displayTitle(section.title)}</h3>}
          <FormattedBody text={section.body} />
        </section>
      ))}
    </div>
  );
}

function dedupeSections(sections) {
  const seen = new Set();
  return sections.filter(section => {
    const key = displayTitle(section.title).toLowerCase();
    if (key !== "possible explanation") return true;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function sectionClass(kind) {
  return cn(
    "rounded-2xl border border-l-4 p-4",
    kind === "urgent" && "border-red-200 border-l-red-600 bg-red-50",
    kind === "warning" && "border-amber-200 border-l-amber-600 bg-amber-50",
    kind === "triage" && "border-slate-200 border-l-slate-500 bg-slate-50",
    kind === "recommendation" && "border-blue-200 border-l-blue-600 bg-blue-50",
    kind === "screening" && "border-blue-200 border-l-blue-600 bg-blue-50",
    kind === "default" && "border-slate-200 border-l-slate-400 bg-white"
  );
}

function FormattedBody({ text }) {
  const blocks = bodyBlocks(text);
  if (blocks.length === 0) return null;

  return (
    <div className="space-y-3 text-sm leading-6 text-slate-700">
      {blocks.map((block, index) => {
        if (block.type === "list") {
          return (
            <ul className="space-y-2" key={index}>
              {block.items.map((item, itemIndex) => (
                <li className={cn("text-slate-700", isListSubheading(item) ? "mt-3 first:mt-0" : "flex gap-2")} key={`${index}-${itemIndex}`}>
                  {isListSubheading(item) ? (
                    <span className="block text-xs font-black uppercase tracking-wide text-slate-800">{cleanInlineText(item).replace(/:$/, "")}</span>
                  ) : (
                    <>
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
                      <span>{cleanInlineText(item)}</span>
                    </>
                  )}
                </li>
              ))}
            </ul>
          );
        }

        if (block.type === "facts") {
          return (
            <dl className="space-y-2" key={index}>
              {block.items.map((item, itemIndex) => (
                <div className="rounded-xl border border-slate-200 bg-white/70 px-3 py-2" key={`${index}-${itemIndex}`}>
                  <dt className="text-xs font-black uppercase tracking-wide text-slate-500">{item.label}</dt>
                  <dd className="mt-0.5 text-sm font-medium text-slate-800">{cleanInlineText(item.value)}</dd>
                </div>
              ))}
            </dl>
          );
        }

        return (
          <p className="text-sm leading-6 text-slate-700" key={index}>
            {cleanInlineText(block.text)}
          </p>
        );
      })}
    </div>
  );
}

function bodyBlocks(value) {
  const lines = String(value || "")
    .split("\n")
    .map(line => line.trim())
    .filter(Boolean);
  const blocks = [];
  let paragraph = [];
  let list = [];
  let facts = [];

  function flushParagraph() {
    if (paragraph.length) {
      blocks.push({ type: "paragraph", text: paragraph.join(" ") });
      paragraph = [];
    }
  }

  function flushList() {
    if (list.length) {
      blocks.push({ type: "list", items: list });
      list = [];
    }
  }

  function flushFacts() {
    if (facts.length) {
      blocks.push({ type: "facts", items: facts });
      facts = [];
    }
  }

  lines.forEach(line => {
    const bullet = line.match(/^[-*•]\s+(.+)$/) || line.match(/^\d+\.\s+(.+)$/);
    const fact = line.match(/^([A-Za-z][A-Za-z\s/+()-]{2,42}):\s+(.+)$/);

    if (bullet) {
      flushParagraph();
      flushFacts();
      list.push(bullet[1]);
      return;
    }

    if (fact && !line.toLowerCase().startsWith("reason:")) {
      flushParagraph();
      flushList();
      facts.push({ label: fact[1], value: fact[2] });
      return;
    }

    flushList();
    flushFacts();
    paragraph.push(line);
  });

  flushParagraph();
  flushList();
  flushFacts();
  return blocks;
}

function legacyCleanInlineText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/\s*\[\d+\]/g, "")
    .replace(/\s*\{\d+\}/g, "")
    .replace(/\s*\(\s*\d+\s*\)/g, "")
    .replace(/^\s*[-*•]\s+/, "")
    .replace(/\s+([.,;:])/g, "$1")
    .trim();
}

function isListSubheading(value) {
  const text = cleanInlineText(value);
  return /^[A-Za-z][A-Za-z\s/+()-]{2,42}:$/.test(text);
}

function TypingIndicator() {
  return (
    <div className="mb-5 flex gap-3">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-teal-50 text-xs font-black text-teal-800 ring-1 ring-teal-100">OC</div>
      <div className="flex min-h-12 items-center gap-2 rounded-3xl border border-slate-200 bg-white px-5">
        <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:120ms]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:240ms]" />
      </div>
    </div>
  );
}

const knownTitles = [
  "OcuAI Screening Support Result",
  "OcuAI Screening Support Report",
  "Text-only triage mode",
  "Screening Status",
  "Reason",
  "Image-text consistency note",
  "Patient-facing result",
  "Input note",
  "Internal screening note",
  "Reported Symptoms",
  "Image-only model evidence",
  "Image + symptom fusion evidence",
  "Recommended action",
  "Knowledge Base Evidence",
  "Retrieved passages used for source-grounded answering:",
  "Trusted Web Evidence",
  "AI Screening Impression",
  "Model Score",
  "Analysis Method",
  "What This Condition Means",
  "Why The Model May Have Predicted This",
  "Common Symptoms",
  "Causes And Risk Factors",
  "Treatment And Management",
  "Knowledge Base Context",
  "Clinical Recommendation",
  "Triage guidance",
];

function parseResponse(value) {
  const lines = String(value || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const sections = [];
  let title = "";
  let body = [];

  function push() {
    const normalized = normalizeSection(title, body.join("\n").trim());
    if (normalized.title || normalized.body) sections.push(normalized);
    title = "";
    body = [];
  }

  lines.forEach(line => {
    const clean = cleanHeadingCandidate(line);
    if (clean === "---") {
      push();
      return;
    }
    const detected = knownTitles.find(item => clean.toLowerCase().startsWith(item.toLowerCase()));
    if (detected) {
      push();
      title = detected;
      const remainder = clean.slice(detected.length).replace(/^:\s*/, "").trim();
      if (remainder) body.push(remainder);
    } else {
      body.push(line);
    }
  });
  push();
  return sections.length ? sections : [{ title: "", body: String(value || ""), kind: "default" }];
}

function cleanHeadingCandidate(value) {
  return String(value || "")
    .trim()
    .replace(/^>\s*/, "")
    .replace(/^#{1,6}\s*/, "")
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/^\d+\.\s*/, "")
    .trim();
}

function normalizeSection(title, body) {
  const kind = classify(title, body);
  if (kind === "hidden" || kind === "evidence") return { title, body: "", kind };
  if (!body && title && shouldHideEmptyTitle(title)) return { title, body: "", kind: "hidden" };
  if (kind === "triage") {
    return {
      title,
      body: summarizeTriageBody(body),
      kind,
    };
  }
  return { title, body, kind };
}

function shouldHideEmptyTitle(title) {
  const lower = String(title || "").toLowerCase();
  return lower.includes("ocuai screening support result") || lower.includes("screening status");
}

function classify(title, body) {
  const titleText = String(title || "").toLowerCase();
  const text = `${title}\n${body}`.toLowerCase();
  if (
    titleText.includes("ocuai screening support report")
    || titleText.includes("ai screening impression")
    || titleText.includes("model score")
    || titleText.includes("analysis method")
    || titleText.includes("reported symptoms")
    || titleText.includes("image-only model evidence")
    || titleText.includes("image + symptom fusion evidence")
    || titleText.includes("input note")
    || titleText.includes("internal screening note")
  ) return "hidden";
  if (titleText.includes("text-only triage mode")) return "triage";
  if (
    titleText.includes("knowledge base evidence")
    || titleText.includes("retrieved passages")
    || titleText.includes("trusted web evidence")
    || titleText.includes("knowledge base context")
    || titleText.includes("evidence/context")
  ) return "evidence";
  if (text.includes("urgent") || text.includes("emergency") || text.includes("red-flag")) return "urgent";
  if (titleText.includes("image-text consistency note")) return "warning";
  if (text.includes("uncertain") || text.includes("unsupported") || text.includes("conflict") || text.includes("disagree")) return "warning";
  if (text.includes("recommended action") || text.includes("clinical recommendation") || text.includes("ophthalmologist") || text.includes("triage")) return "recommendation";
  if (text.includes("screening status")) return "screening";
  return "default";
}

function displayTitle(title) {
  const clean = cleanInlineText(String(title || "").replace(/^\d+\.\s*/, "")).replace(/:$/, "");
  const lower = clean.toLowerCase();
  if (lower.includes("text-only triage mode")) return "Text-only guidance";
  if (lower.includes("screening status") || lower.includes("screening impression")) return "Screening impression";
  if (lower.includes("reason") || lower.includes("what this condition means") || lower.includes("why the model")) return "Possible explanation";
  if (lower.includes("urgent") || lower.includes("red-flag")) return "Red flags";
  if (lower.includes("recommended") || lower.includes("clinical recommendation")) return "Recommended next step";
  if (lower.includes("knowledge base") || lower.includes("retrieved passages") || lower.includes("context")) return "Evidence/context";
  return clean;
}

function summarizeTriageBody(body) {
  const text = String(body || "");
  const urgencyLine = text
    .split("\n")
    .map(line => line.trim())
    .find(line => line.toLowerCase().startsWith("urgency flag:"));

  const lines = ["No eye image was uploaded. This answer is educational guidance, not a diagnosis."];
  if (urgencyLine) {
    lines.push(urgencyLine.replace("Urgency flag:", "Urgency:"));
  }
  return lines.join("\n");
}

function stripVisibleNumbers(value) {
  return String(value || "")
    .replace(/\b\d+\.\s+/g, "")
    .replace(/\s*\[\d+\]/g, "")
    .replace(/\s*\{\d+\}/g, "")
    .replace(/\s*\(\s*\d+\s*\)/g, "");
}

function cleanInlineText(value) {
  return stripVisibleNumbers(value)
    .replace(/\*\*/g, "")
    .replace(/^\s*[-*•]\s+/, "")
    .replace(/\s+([.,;:])/g, "$1")
    .trim();
}

function formatTime() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function classifyChatOutcome(responseText, { hadImage = false, userText = "", mode = "text-only" } = {}) {
  const text = String(responseText || "");
  const lower = text.toLowerCase();
  const imageRejected = hadImage && isRejectedImageResponse(text);
  const technicalError = lower.includes("inference error") || lower.includes("model unavailable") || lower.includes("could not process your request");
  const condition = hadImage && !imageRejected ? extractScreeningCondition(text) : "";
  const confidence = condition ? extractModelConfidence(text) : null;
  const urgent = [
    "urgent symptom", "urgency flag", "seek urgent", "emergency", "sudden vision loss",
    "severe eye pain", "chemical exposure", "curtain-like", "red flag",
  ].some(term => lower.includes(term));
  const uncertain = lower.includes("uncertain / unsupported")
    || lower.includes("screening status: uncertain")
    || lower.includes("strongly disagree");
  const acceptedImage = hadImage && !imageRejected && !technicalError && Boolean(condition || uncertain);
  const importantText = isClinicallyImportantText(userText);

  return {
    mode,
    outcome: imageRejected ? "image_rejected" : technicalError ? "processing_error" : uncertain ? "uncertain" : acceptedImage ? "screening_completed" : "guidance",
    image_rejected: imageRejected,
    accepted_image: acceptedImage,
    condition: condition || null,
    model_confidence: confidence,
    urgent,
    uncertain,
    include_in_summary: !imageRejected && !technicalError && (acceptedImage || uncertain || urgent || importantText),
  };
}

function isRejectedImageResponse(value) {
  const text = String(value || "").toLowerCase();
  return text.includes("screening status: image rejected")
    || text.includes("image rejected before cnn/multimodal analysis")
    || text.includes("does not appear to be a supported retinal/fundus scan")
    || text.includes("outside the accepted fundus feature range")
    || text.includes("was not confirmed as a clear retinal/fundus scan");
}

function extractScreeningCondition(value) {
  const text = String(value || "");
  const patterns = [
    /AI Screening Impression:\s*\**([^\n*]+)/i,
    /Predicted Condition:\s*\**([^\n*]+)/i,
    /(?:\*\*)?Diagnosis:(?:\*\*)?\s*\**([^\n*]+)/i,
    /Top result:\s*([^\n(]+)/i,
    /fusion result:\s*([^\n(.;]+)/i,
  ];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    const normalized = normalizeConditionName(match?.[1]);
    if (normalized) return normalized;
  }
  return "";
}

function normalizeConditionName(value) {
  const candidate = String(value || "").replace(/[*_#]/g, "").replace(/\s+/g, " ").trim().toLowerCase();
  if (candidate.includes("diabetic retinopathy")) return "Diabetic Retinopathy";
  if (candidate.includes("retinal disease")) return "Retinal Disease";
  if (candidate.includes("glaucoma")) return "Glaucoma";
  if (candidate.includes("cataract")) return "Cataract";
  if (/^normal\b/.test(candidate)) return "Normal";
  return "";
}

function extractModelConfidence(value) {
  const match = String(value || "").match(/(?:Model Score|Confidence):\s*\**\s*(\d+(?:\.\d+)?)\s*%/i);
  return match ? Number(match[1]) : null;
}

function isClinicallyImportantText(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim().toLowerCase();
  if (!text || ["hi", "hello", "hey", "good morning", "good evening", "thanks", "thank you"].includes(text)) return false;
  return [
    "vision", "eye", "glaucoma", "cataract", "retina", "retinal", "diabetic",
    "blurry", "blurred", "pressure", "pain", "floaters", "flashes", "redness",
    "itch", "dry", "watery", "night", "light", "headache", "trauma", "chemical",
  ].some(term => text.includes(term));
}

function isSummaryEligibleRow(row) {
  const metadata = row?.metadata && typeof row.metadata === "object" ? row.metadata : {};
  if (metadata.image_rejected || metadata.outcome === "image_rejected" || isRejectedImageResponse(row?.content)) return false;
  if (metadata.include_in_summary === false) return false;
  if (metadata.include_in_summary === true) return true;
  if (row?.role === "user") return isClinicallyImportantText(row.content);

  const legacyImageMode = String(metadata.mode || "").toLowerCase().includes("image");
  const legacyOutcome = classifyChatOutcome(row?.content, { hadImage: legacyImageMode, mode: metadata.mode });
  return legacyOutcome.accepted_image || legacyOutcome.uncertain || legacyOutcome.urgent;
}

function rowClinicalMetadata(row) {
  const metadata = row?.metadata && typeof row.metadata === "object" ? row.metadata : {};
  if (metadata.condition || metadata.accepted_image || metadata.uncertain || metadata.urgent) return metadata;
  const legacyImageMode = String(metadata.mode || "").toLowerCase().includes("image");
  return { ...metadata, ...classifyChatOutcome(row?.content, { hadImage: legacyImageMode, mode: metadata.mode }) };
}

function toSummaryMessage(row) {
  const metadata = rowClinicalMetadata(row);
  let content = String(row?.content || "").replace(/\[image uploaded\]/gi, "").replace(/\s+/g, " ").trim();

  if (row?.role === "assistant") {
    const score = Number.isFinite(Number(metadata.model_confidence)) ? ` (${Number(metadata.model_confidence).toFixed(1)}% model score)` : "";
    if (metadata.condition) {
      content = `Accepted eye-image screening finding: ${metadata.condition}${score}. This is a screening result, not a confirmed diagnosis.`;
    } else if (metadata.uncertain) {
      content = "Eye-image screening was uncertain or conflicting and professional review was recommended.";
    } else if (metadata.urgent) {
      content = "The conversation contained an urgent eye-health warning and recommended prompt professional care.";
    } else {
      content = "";
    }
  } else if (!content && metadata.accepted_image) {
    content = "A retinal/fundus image was accepted for eye screening.";
  }

  return {
    role: row.role,
    content: content.slice(0, 700),
    image_present: Boolean(row.image_present && metadata.accepted_image),
    created_at: row.created_at,
    metadata: {
      condition: metadata.condition || null,
      model_confidence: metadata.model_confidence ?? null,
      accepted_image: Boolean(metadata.accepted_image),
      urgent: Boolean(metadata.urgent),
      uncertain: Boolean(metadata.uncertain),
      include_in_summary: true,
    },
  };
}

function enrichFallbackSummary(summary, rows) {
  const result = summary && typeof summary === "object" ? summary : {};
  const isFallback = result.generation_status === "fallback"
    || String(result.summary_text || "").startsWith("This is an automatic non-diagnostic summary");
  if (!isFallback) return result;

  const messages = Array.isArray(rows) ? rows : [];
  const summaryMessages = messages.map(toSummaryMessage).filter(message => message.content);
  const combined = summaryMessages.map(message => message.content).join(" ").toLowerCase();
  const concerns = summaryMessages
    .filter(row => row.role === "user")
    .map(row => String(row.content || "").replace(/\[image uploaded\]/gi, "").replace(/\s+/g, " ").trim())
    .filter(value => value && !["hi", "hello", "hey", "good morning", "good evening"].includes(value.toLowerCase()));

  const symptoms = uniqueMatches(combined, [
    ["eye pressure", "Eye pressure"],
    ["side vision loss", "Gradual side-vision loss"],
    ["peripheral vision", "Peripheral-vision changes"],
    ["blurry vision", "Blurry vision"],
    ["blurred vision", "Blurred vision"],
    ["vision loss", "Vision loss"],
    ["eye pain", "Eye pain"],
    ["floaters", "Floaters"],
    ["flashes", "Flashes"],
    ["red eye", "Red eye"],
  ]);
  const topics = uniqueMatches(combined, [
    ["glaucoma", "Glaucoma"],
    ["cataract", "Cataract"],
    ["diabetic retinopathy", "Diabetic retinopathy"],
    ["retinal disease", "Retinal disease"],
    ["eye pressure", "Eye pressure"],
    ["vision loss", "Vision changes"],
    ["fundus", "Fundus-image screening"],
    ["screening", "AI screening support"],
  ]);
  const redFlags = [];
  if (["sudden vision loss", "severe eye pain", "chemical exposure", "curtain", "trauma"].some(term => combined.includes(term))) {
    redFlags.push("An urgent eye-health warning sign was reported in the saved chats");
  } else if (combined.includes("vision loss")) {
    redFlags.push("Reported vision loss or visual-field loss needs prompt professional assessment");
  }

  const screeningFindings = [];
  messages.forEach(row => {
    if (row.role !== "assistant") return;
    const metadata = rowClinicalMetadata(row);
    if (metadata.condition) {
      const score = Number.isFinite(Number(metadata.model_confidence)) ? ` (${Number(metadata.model_confidence).toFixed(1)}% model score)` : "";
      screeningFindings.push(`Accepted image screening suggested ${metadata.condition}${score}; this is not a confirmed diagnosis`);
      if (metadata.condition !== "Normal") {
        redFlags.push(`Image screening suggested ${metadata.condition}; arrange professional confirmation`);
      }
    } else if (metadata.uncertain) {
      screeningFindings.push("An image-screening result was uncertain or conflicting and needs professional review");
    }
  });
  const imageHistory = [...new Set(screeningFindings)];
  const acceptedUploadCount = messages.filter(row => Boolean(row.image_present) && rowClinicalMetadata(row).accepted_image).length;
  if (acceptedUploadCount && imageHistory.length === 0) {
    imageHistory.push(`${acceptedUploadCount} retinal/fundus image upload(s) were accepted for screening`);
  }

  return {
    ...result,
    summary_text: concerns.length || imageHistory.length
      ? `Important saved eye-health information: ${[
          concerns.length ? `reported concerns: ${concerns.slice(-4).join("; ")}` : "",
          imageHistory.length ? `screening findings: ${imageHistory.slice(-3).join("; ")}` : "",
        ].filter(Boolean).join(". ").slice(0, 700)}`
      : "No clinically important patient-reported concerns or accepted screening findings were found.",
    symptoms,
    topics,
    red_flags: [...new Set(redFlags)],
    image_history: imageHistory,
    recommended_next_steps: redFlags.length || imageHistory.some(item => !item.includes("Normal"))
      ? ["Use this summary only as a preparation aid for professional eye care.", "Arrange prompt or urgent assessment by a licensed eye-care professional based on symptom severity."]
      : ["Use this summary only as a preparation aid for professional eye care.", "Discuss persistent or worsening eye symptoms with a licensed eye-care professional."],
    generation_status: "fallback",
  };
}

function uniqueMatches(text, patterns) {
  return [...new Set(patterns.filter(([phrase]) => text.includes(phrase)).map(([, label]) => label))];
}

function titleFromMessage(value) {
  const clean = String(value || "Eye image screening").replace(/\s+/g, " ").trim();
  return clean.length > 44 ? `${clean.slice(0, 44)}...` : clean;
}

function formatStoredTime(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function App() {
  return window.location.pathname.startsWith("/bot") ? <AssistantPage /> : <LandingPage />;
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
