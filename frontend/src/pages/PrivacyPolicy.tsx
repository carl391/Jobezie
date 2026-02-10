import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/"
            className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent"
          >
            Jobezie
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
          <p className="text-sm text-gray-500 mb-8">Last updated: February 2026</p>

          <div className="prose prose-gray max-w-none space-y-8">
            {/* Introduction */}
            <section>
              <p className="text-gray-600 leading-relaxed">
                Jobezie ("we," "us," or "our") is an AI-powered career assistant that helps job seekers optimize their resumes, manage recruiter relationships, and discover career opportunities. This Privacy Policy explains how we collect, use, disclose, and protect your personal information when you use our platform at jobezie.com (the "Service").
              </p>
              <p className="text-gray-600 leading-relaxed">
                By using Jobezie, you agree to the collection and use of information in accordance with this policy. If you do not agree, please do not use the Service.
              </p>
            </section>

            {/* 1. Information We Collect */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">1. Information We Collect</h2>

              <h3 className="text-lg font-medium text-gray-800 mt-4">Account Information</h3>
              <p className="text-gray-600">When you register, we collect your name, email address, and password (stored as a secure hash). You may also provide a phone number, location, and LinkedIn profile URL.</p>

              <h3 className="text-lg font-medium text-gray-800 mt-4">Career Data</h3>
              <p className="text-gray-600">To provide personalized recommendations, we collect career-related information including:</p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li>Resumes you upload (PDF/DOCX files and parsed text content)</li>
                <li>Career stage, target roles, industries, and skills</li>
                <li>Recruiter contact information you enter</li>
                <li>Messages you compose or generate using AI</li>
                <li>Location preferences and salary expectations</li>
              </ul>

              <h3 className="text-lg font-medium text-gray-800 mt-4">Usage Data</h3>
              <p className="text-gray-600">We automatically collect information about how you interact with the Service, including pages visited, features used, and actions taken. This helps us improve the platform.</p>

              <h3 className="text-lg font-medium text-gray-800 mt-4">AI-Generated Content</h3>
              <p className="text-gray-600">When you use AI features (resume optimization, message generation, career coaching), we process your inputs and store the generated outputs to provide the Service and improve your experience.</p>
            </section>

            {/* 2. How We Use Your Information */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">2. How We Use Your Information</h2>
              <p className="text-gray-600">We use the information we collect to:</p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li>Provide and maintain the Service, including AI-powered features</li>
                <li>Calculate scores using our algorithms (ATS scoring, career readiness, recruiter fit, etc.)</li>
                <li>Generate personalized recommendations and career coaching</li>
                <li>Match your profile with labor market opportunities using O*NET and BLS data</li>
                <li>Process payments and manage your subscription</li>
                <li>Send transactional emails (verification, password reset, account notifications)</li>
                <li>Improve the Service based on usage patterns</li>
              </ul>
            </section>

            {/* 3. AI Data Processing */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">3. AI Data Processing Disclosure</h2>
              <p className="text-gray-600">
                Jobezie uses artificial intelligence to provide resume scoring, message generation, career coaching, and other features. When you use these features:
              </p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li>Your relevant data (resume text, career information, conversation messages) is sent to AI service providers for processing</li>
                <li>We use Anthropic (Claude) as our primary AI provider and OpenAI (GPT-4) as a secondary provider</li>
                <li>AI-generated scores, recommendations, and content are <strong>guidance only</strong> and do not constitute professional career advice or employment decisions</li>
                <li>We do not use your personal data to train AI models. Data is processed for your individual requests only</li>
                <li>All scoring algorithms are deterministic and auditable — they do not use AI</li>
              </ul>
            </section>

            {/* 4. Third-Party Services */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">4. Third-Party Services</h2>
              <p className="text-gray-600">We share data with the following service providers, solely to operate the Service:</p>
              <div className="overflow-x-auto mt-3">
                <table className="w-full text-sm text-gray-600">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 pr-4 font-medium text-gray-800">Provider</th>
                      <th className="text-left py-2 pr-4 font-medium text-gray-800">Purpose</th>
                      <th className="text-left py-2 font-medium text-gray-800">Data Shared</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    <tr><td className="py-2 pr-4">Anthropic (Claude)</td><td className="py-2 pr-4">AI analysis and coaching</td><td className="py-2">Resume text, career data, chat messages</td></tr>
                    <tr><td className="py-2 pr-4">OpenAI (GPT-4)</td><td className="py-2 pr-4">AI content generation (fallback)</td><td className="py-2">Resume text, career data</td></tr>
                    <tr><td className="py-2 pr-4">Stripe</td><td className="py-2 pr-4">Payment processing</td><td className="py-2">Email, payment method (we never see full card numbers)</td></tr>
                    <tr><td className="py-2 pr-4">SendGrid</td><td className="py-2 pr-4">Transactional email</td><td className="py-2">Email address, name</td></tr>
                    <tr><td className="py-2 pr-4">Railway</td><td className="py-2 pr-4">Hosting infrastructure</td><td className="py-2">All data (encrypted at rest and in transit)</td></tr>
                  </tbody>
                </table>
              </div>
              <p className="text-gray-600 mt-3">We do <strong>not</strong> sell your personal information to any third party.</p>
            </section>

            {/* 5. Your Rights */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">5. Your Rights</h2>
              <p className="text-gray-600">You have the right to:</p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li><strong>Access:</strong> Request a copy of the personal data we hold about you</li>
                <li><strong>Correction:</strong> Update or correct inaccurate information via your Settings page</li>
                <li><strong>Deletion:</strong> Request deletion of your account and associated data</li>
                <li><strong>Portability:</strong> Export your data in a machine-readable format</li>
                <li><strong>Opt-out of automated scoring:</strong> Request that algorithmic scores not be used for your account</li>
              </ul>
              <p className="text-gray-600 mt-3">To exercise these rights, contact us at privacy@jobezie.com or use the Data & Privacy section in your Settings.</p>

              <h3 className="text-lg font-medium text-gray-800 mt-4">California Privacy Rights (CCPA)</h3>
              <p className="text-gray-600">
                If you are a California resident, you have additional rights under the California Consumer Privacy Act (CCPA), including the right to know what personal information is collected, the right to delete your information, and the right to opt-out of the sale of your information. We do not sell personal information. To make a CCPA request, email privacy@jobezie.com.
              </p>
            </section>

            {/* 6. Data Retention */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">6. Data Retention</h2>
              <p className="text-gray-600">
                We retain your data while your account is active. If you delete your account, we will delete your personal data within 30 days, except where we are required to retain it by law. Anonymized usage data may be retained for analytics purposes.
              </p>
            </section>

            {/* 7. Security */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">7. Security Measures</h2>
              <p className="text-gray-600">We protect your data with:</p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li>Passwords hashed with bcrypt (never stored in plain text)</li>
                <li>JWT-based authentication with short-lived access tokens</li>
                <li>HTTPS encryption for all data in transit</li>
                <li>Input validation and sanitization to prevent injection attacks</li>
                <li>Rate limiting to prevent abuse</li>
                <li>Database encryption at rest</li>
              </ul>
            </section>

            {/* 8. Children's Privacy */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">8. Children's Privacy</h2>
              <p className="text-gray-600">
                Jobezie is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13. If you believe a child under 13 has provided us with personal information, please contact us at privacy@jobezie.com and we will promptly delete it.
              </p>
            </section>

            {/* 9. Cookies */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">9. Cookies and Local Storage</h2>
              <p className="text-gray-600">
                We use browser local storage to maintain your authentication session and remember your preferences (such as dismissed notifications and UI settings). We do not use third-party tracking cookies. Essential cookies are required for the Service to function.
              </p>
            </section>

            {/* 10. Changes */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">10. Changes to This Policy</h2>
              <p className="text-gray-600">
                We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the updated policy on this page and updating the "Last updated" date. Your continued use of the Service after changes constitutes acceptance of the updated policy.
              </p>
            </section>

            {/* 11. Contact */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">11. Contact Us</h2>
              <p className="text-gray-600">
                If you have questions about this Privacy Policy or wish to exercise your data rights, contact us at:
              </p>
              <p className="text-gray-600 mt-2">
                <strong>Email:</strong> privacy@jobezie.com
              </p>
            </section>
          </div>

          {/* Back link */}
          <div className="mt-10 pt-6 border-t border-gray-200">
            <Link
              to="/"
              className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to Jobezie
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
