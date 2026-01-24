import { useState } from 'react';
import axios from 'axios';
import { Mail, AlertTriangle, Send, Bug, Loader2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

type ContactMode = 'general' | 'issue';

export function ContactPage() {
    const [mode, setMode] = useState<ContactMode>('general');

    // Check URL hash to set initial mode (e.g. /contact#report)
    useState(() => {
        if (window.location.hash === '#report') {
            setMode('issue');
        }
    });

    return (
        <div className="max-w-4xl mx-auto p-6 py-12 space-y-8">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">Get in Touch</h1>
                <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                    We welcome your feedback, questions, and bug reports to help improve the ALS/FTD Research Dashboard.
                </p>
            </div>

            {/* Mode Toggle */}
            <div className="flex justify-center">
                <div className="inline-flex h-12 items-center justify-center rounded-lg bg-secondary/50 p-1 text-muted-foreground">
                    <button
                        onClick={() => setMode('general')}
                        className={`inline-flex items-center justify-center whitespace-nowrap rounded-md px-6 py-2 text-sm font-medium transition-all ${mode === 'general'
                                ? 'bg-background text-foreground shadow-sm'
                                : 'hover:bg-background/50 hover:text-foreground'
                            }`}
                    >
                        <Mail className="mr-2 h-4 w-4" />
                        General Inquiry
                    </button>
                    <button
                        onClick={() => setMode('issue')}
                        className={`inline-flex items-center justify-center whitespace-nowrap rounded-md px-6 py-2 text-sm font-medium transition-all ${mode === 'issue'
                                ? 'bg-background text-foreground shadow-sm'
                                : 'hover:bg-background/50 hover:text-foreground'
                            }`}
                    >
                        <Bug className="mr-2 h-4 w-4" />
                        Report an Issue
                    </button>
                </div>
            </div>

            {/* Form Container */}
            <div className="glass-panel p-8 rounded-2xl border border-border/50 shadow-lg">
                {mode === 'general' ? <GeneralContactForm /> : <IssueReportForm />}
            </div>
        </div>
    );
}

function GeneralContactForm() {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const formData = new FormData(e.currentTarget);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message'),
        };

        try {
            await axios.post('/api/contact/', data);
            setSuccess(true);
        } catch (err) {
            setError('Failed to send message. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                <div className="h-16 w-16 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-500 mb-2">
                    <CheckCircle2 className="h-8 w-8" />
                </div>
                <h3 className="text-2xl font-bold">Message Sent!</h3>
                <p className="text-muted-foreground">Thank you for contacting us. We will get back to you shortly.</p>
                <Button onClick={() => setSuccess(false)} variant="outline" className="mt-4">
                    Send Another Message
                </Button>
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label htmlFor="name" className="text-sm font-medium">Name</label>
                    <Input id="name" name="name" required placeholder="Dr. Jane Doe" />
                </div>
                <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-medium">Email</label>
                    <Input id="email" name="email" type="email" required placeholder="jane@research.org" />
                </div>
            </div>

            <div className="space-y-2">
                <label htmlFor="subject" className="text-sm font-medium">Subject</label>
                <Input id="subject" name="subject" required placeholder="Research collaboration inquiry" />
            </div>

            <div className="space-y-2">
                <label htmlFor="message" className="text-sm font-medium">Message</label>
                <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="How can we help you?"
                />
            </div>

            {error && (
                <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...</> : <><Send className="mr-2 h-4 w-4" /> Send Message</>}
            </Button>
        </form>
    );
}

function IssueReportForm() {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const formData = new FormData(e.currentTarget);
        const data = {
            title: formData.get('title'),
            description: formData.get('description'),
            steps_to_reproduce: formData.get('steps'),
            browser_info: navigator.userAgent,
            reported_by: formData.get('email') || null,
        };

        try {
            await axios.post('/api/contact/report-issue', data);
            setSuccess(true);
        } catch (err) {
            setError('Failed to submit report. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                <div className="h-16 w-16 bg-blue-500/10 rounded-full flex items-center justify-center text-blue-500 mb-2">
                    <Bug className="h-8 w-8" />
                </div>
                <h3 className="text-2xl font-bold">Report Submitted</h3>
                <p className="text-muted-foreground">Thank you for helping us improve the platform. We'll look into this issue immediately.</p>
                <Button onClick={() => setSuccess(false)} variant="outline" className="mt-4">
                    Report Another Issue
                </Button>
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto">
            <div className="space-y-2">
                <label htmlFor="title" className="text-sm font-medium">Issue Summary</label>
                <Input id="title" name="title" required placeholder="e.g., Search filter not updating results" />
            </div>

            <div className="space-y-2">
                <label htmlFor="description" className="text-sm font-medium">Description</label>
                <textarea
                    id="description"
                    name="description"
                    required
                    rows={4}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Describe what happened..."
                />
            </div>

            <div className="space-y-2">
                <label htmlFor="steps" className="text-sm font-medium">Steps to Reproduce (Optional)</label>
                <textarea
                    id="steps"
                    name="steps"
                    rows={3}
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="1. Go to Trial Finder&#10;2. Select Phase 3&#10;3. Click..."
                />
            </div>

            <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">Your Email (Optional)</label>
                <Input id="email" name="email" type="email" placeholder="In case we need more details..." />
                <p className="text-[10px] text-muted-foreground">We'll automatically capture your browser version ({navigator.userAgent.split(') ')[0]}) to help debugging.</p>
            </div>

            {error && (
                <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Submitting...</> : <><Bug className="mr-2 h-4 w-4" /> Submit Report</>}
            </Button>
        </form>
    );
}
