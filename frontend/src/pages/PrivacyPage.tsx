import { Shield, Lock, FileText, Info } from 'lucide-react';

export function PrivacyPage() {
    return (
        <div className="max-w-4xl mx-auto p-6 py-12 space-y-12">
            {/* Header */}
            <div className="space-y-4 text-center">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">Legal Information</h1>
                <p className="text-muted-foreground text-lg">
                    Privacy Policy, Terms of Service, and Cookie Information for the ALS/FTD Research Dashboard.
                </p>
            </div>

            {/* Privacy Policy */}
            <section id="privacy" className="glass-panel p-8 rounded-2xl space-y-6">
                <div className="flex items-center gap-3 text-primary">
                    <Shield className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">Privacy Policy</h2>
                </div>
                <div className="space-y-4 text-muted-foreground leading-relaxed">
                    <p>
                        Your privacy is important to us. This Privacy Policy explains how the ALS/FTD Research Dashboard 
                        collects, uses, and protects information when you use our platform.
                    </p>
                    <h3 className="font-semibold text-foreground italic">Data Collection</h3>
                    <p>
                        We do not collect personal identifying information (PII) from casual visitors. 
                        The dashboard is primarily a read-only research tool. Any data you enter into 
                        the Query Builder is processed locally or on our server to return results but is 
                        not stored permanently linked to your identity.
                    </p>
                    <h3 className="font-semibold text-foreground italic">External Links</h3>
                    <p>
                        Our platform links to ClinicalTrials.gov and other research institutions. 
                        We are not responsible for the privacy practices of these external sites.
                    </p>
                </div>
            </section>

            {/* Terms of Service */}
            <section id="terms" className="glass-panel p-8 rounded-2xl space-y-6">
                <div className="flex items-center gap-3 text-primary">
                    <FileText className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">Terms of Service</h2>
                </div>
                <div className="space-y-4 text-muted-foreground leading-relaxed">
                    <p>
                        By using this platform, you agree to the following terms:
                    </p>
                    <ul className="list-disc pl-5 space-y-2">
                        <li>The data provided is for informational and research purposes only.</li>
                        <li>It does not constitute medical advice or clinical recommendations.</li>
                        <li>You may not use this platform for any commercial purpose without prior written consent.</li>
                        <li>Automated scraping of this dashboard is prohibited to protect server resources.</li>
                    </ul>
                </div>
            </section>

            {/* Cookie Settings */}
            <section id="cookies" className="glass-panel p-8 rounded-2xl space-y-6">
                <div className="flex items-center gap-3 text-primary">
                    <Lock className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">Cookie Settings</h2>
                </div>
                <div className="space-y-4 text-muted-foreground leading-relaxed">
                    <p>
                        We use minimal cookies to enhance your experience:
                    </p>
                    <ul className="list-disc pl-5 space-y-2">
                        <li><span className="text-foreground font-medium">Theme Preference:</span> To remember if you prefer Dark or Light mode.</li>
                        <li><span className="text-foreground font-medium">Session Management:</span> To maintain your connection to our analytics backend.</li>
                    </ul>
                    <p>
                        We do not use tracking or advertising cookies. You can manage cookies through your browser settings.
                    </p>
                </div>
            </section>

            {/* Contact */}
            <div className="bg-secondary/20 p-6 rounded-xl border border-border flex items-start gap-4">
                <Info className="h-5 w-5 text-primary mt-1" />
                <div className="space-y-1">
                    <p className="text-sm font-medium">Questions about our legal terms?</p>
                    <p className="text-sm text-muted-foreground">
                        Please contact the project maintainer at <a href="mailto:tuckerolson13@gmail.com" className="text-primary hover:underline">tuckerolson13@gmail.com</a>
                    </p>
                </div>
            </div>
        </div>
    );
}
