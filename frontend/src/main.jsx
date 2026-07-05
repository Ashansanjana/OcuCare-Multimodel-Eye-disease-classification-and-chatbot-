import React, { useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bot,
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
  ShieldAlert,
  Sparkles,
  Stethoscope,
  Upload,
  X,
} from "lucide-react";
import "./styles.css";
import heroImage from "./assets/ophthalmology-hero.png";

const urgentText =
  "Seek immediate care for sudden vision loss, severe pain, injury, chemical exposure, flashes, floaters, or a curtain over vision.";

const quickPrompts = [
  "What should I do for blurry vision and eye pain?",
  "Explain glaucoma symptoms in simple language.",
  "When should floaters be treated as urgent?",
];

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
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Ask about eye symptoms, conditions, or care. You may upload an eye image for screening support. This tool is informational and cannot confirm a diagnosis.",
      time: "OcuCare Assistant",
    },
  ]);
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef(null);
  const activeMode = file && text.trim() ? "Image + symptoms" : file ? "Image-only" : "Text-only";

  const workflowList = useMemo(
    () => ["Source-grounded education", "Class-limited image screening", "Image-text contradiction check", "Urgent symptom escalation"],
    []
  );

  function resetFile() {
    setFile(null);
    setPreview("");
    if (fileInputRef.current) fileInputRef.current.value = "";
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

    setMessages(prev => [...prev, { role: "user", text: cleanText, image: preview, time: formatTime() }]);
    setText("");
    resetFile();
    setBusy(true);

    try {
      const response = await fetch("/get", { method: "POST", body: formData });
      if (!response.ok) throw new Error("Request failed");
      const data = await response.text();
      setMessages(prev => [...prev, { role: "assistant", text: data, time: `${formatTime()} - OcuCare` }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", text: "We could not process your request. Please try again.", time: formatTime(), error: true }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <Header assistant />
      <main className="grid h-[calc(100vh-73px)] gap-4 p-4 lg:grid-cols-[310px_minmax(460px,1fr)_320px] lg:p-5">
        <aside className="glass-panel overflow-y-auto rounded-3xl p-5">
          <Badge tone="teal"><Bot size={14} /> Assistant online</Badge>
          <h1 className="mt-5 text-3xl font-black leading-tight text-slate-950">Clinical support workspace</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">A focused workspace for patient education, image-supported screening, and safety-aware next steps.</p>

          <Card className="mt-6 border-teal-200 bg-teal-50 p-5">
            <span className="text-xs font-black uppercase tracking-wide text-teal-800">Current mode</span>
            <strong className="mt-2 block text-2xl font-black text-slate-950">{activeMode}</strong>
            <p className="mt-2 text-sm text-slate-600">
              {activeMode === "Image + symptoms"
                ? "The system will compare image evidence with symptom text."
                : activeMode === "Image-only"
                  ? "The image model will be treated as screening evidence only."
                  : "The assistant will answer as text-only educational triage."}
            </p>
          </Card>

          <div className="mt-6">
            <h2 className="text-sm font-black uppercase tracking-wide text-slate-500">Workflow coverage</h2>
            <div className="mt-3 space-y-2">
              {workflowList.map(item => (
                <div key={item} className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3 text-sm text-slate-700">
                  <CheckCircle2 className="text-teal-700" size={17} />
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-900">
            <div className="flex items-center gap-2 font-black"><AlertTriangle size={18} /> Emergency warning</div>
            <p className="mt-2 leading-6">{urgentText}</p>
          </div>
        </aside>

        <section className="flex min-h-0 flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-950/10">
          <div className="flex items-start justify-between gap-5 border-b border-slate-200 px-5 py-4">
            <div>
              <Badge tone="blue"><Microscope size={14} /> OcuCare assistant</Badge>
              <h2 className="mt-2 text-2xl font-black text-slate-950">Patient guidance chat</h2>
            </div>
            <Badge tone="teal">Research prototype</Badge>
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

        <aside className="space-y-4 overflow-y-auto">
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
            <ReviewItem icon={FileSearch} label="Evidence/context visible" />
            <ReviewItem icon={AlertTriangle} label="Red flags separated" />
            <ReviewItem icon={Stethoscope} label="Next step clearly stated" />
          </Card>
          <Card className="border-amber-200 bg-amber-50 p-5">
            <h2 className="text-lg font-black text-amber-950">Research boundary</h2>
            <p className="mt-2 text-sm leading-6 text-amber-900">Outputs are not medical diagnosis. Keep limitations visible in demos and final presentation.</p>
          </Card>
        </aside>
      </main>
    </div>
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
  const sections = parseResponse(text);
  return (
    <div className="space-y-3">
      {sections.map((section, index) => (
        <section className={sectionClass(section.kind)} key={`${section.title}-${index}`}>
          {section.title && <h3 className="mb-1 text-sm font-black text-slate-950">{displayTitle(section.title)}</h3>}
          <p className="whitespace-pre-wrap text-sm leading-6 text-slate-600">{section.body}</p>
        </section>
      ))}
    </div>
  );
}

function sectionClass(kind) {
  return cn(
    "rounded-2xl border border-l-4 p-3",
    kind === "urgent" && "border-red-200 border-l-red-600 bg-red-50",
    kind === "warning" && "border-amber-200 border-l-amber-600 bg-amber-50",
    kind === "evidence" && "border-teal-200 border-l-teal-600 bg-teal-50",
    kind === "recommendation" && "border-blue-200 border-l-blue-600 bg-blue-50",
    kind === "screening" && "border-blue-200 border-l-blue-600 bg-blue-50",
    kind === "default" && "border-slate-200 border-l-slate-400 bg-white"
  );
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
  "Screening Status:",
  "Reason:",
  "Reported Symptoms:",
  "Image-only model evidence:",
  "Image + symptom fusion evidence:",
  "Recommended action:",
  "Knowledge Base Evidence",
  "Retrieved passages used for source-grounded answering:",
  "AI Screening Impression:",
  "Model Score:",
  "Analysis Method:",
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
    const text = body.join("\n").trim();
    if (title || text) sections.push({ title, body: text, kind: classify(title, text) });
    title = "";
    body = [];
  }

  lines.forEach(line => {
    const clean = line.trim().replace(/^\d+\.\s*/, "");
    if (clean === "---") {
      push();
      return;
    }
    const detected = knownTitles.find(item => clean.startsWith(item));
    if (detected) {
      push();
      title = line.trim();
    } else {
      body.push(line);
    }
  });
  push();
  return sections.length ? sections : [{ title: "", body: String(value || ""), kind: "default" }];
}

function classify(title, body) {
  const text = `${title}\n${body}`.toLowerCase();
  if (text.includes("urgent") || text.includes("emergency") || text.includes("red-flag")) return "urgent";
  if (text.includes("uncertain") || text.includes("unsupported") || text.includes("conflict") || text.includes("disagree")) return "warning";
  if (text.includes("knowledge base evidence") || text.includes("retrieved passages") || text.includes("source:")) return "evidence";
  if (text.includes("recommended action") || text.includes("clinical recommendation") || text.includes("ophthalmologist") || text.includes("triage")) return "recommendation";
  if (text.includes("screening status") || text.includes("screening impression") || text.includes("model score")) return "screening";
  return "default";
}

function displayTitle(title) {
  const clean = String(title || "").replace(/:$/, "");
  const lower = clean.toLowerCase();
  if (lower.includes("screening status") || lower.includes("screening impression")) return "Screening impression";
  if (lower.includes("reason") || lower.includes("what this condition means") || lower.includes("why the model")) return "Possible explanation";
  if (lower.includes("urgent") || lower.includes("red-flag")) return "Red flags";
  if (lower.includes("recommended") || lower.includes("triage") || lower.includes("clinical recommendation")) return "Recommended next step";
  if (lower.includes("knowledge base") || lower.includes("retrieved passages") || lower.includes("context")) return "Evidence/context";
  return clean;
}

function formatTime() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function App() {
  return window.location.pathname.startsWith("/bot") ? <AssistantPage /> : <LandingPage />;
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
