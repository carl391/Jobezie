import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export function TermsOfService() {
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
          <p className="text-sm text-gray-500 mb-8">Last updated: February 2026</p>

          <div className="prose prose-gray max-w-none space-y-8">
            {/* 1. Acceptance */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">1. Acceptance of Terms</h2>
              <p className="text-gray-600 leading-relaxed">
                By accessing or using Jobezie ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not use the Service. We may update these Terms from time to time, and your continued use constitutes acceptance of any changes.
              </p>
            </section>

            {/* 2. Description */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">2. Description of Service</h2>
              <p className="text-gray-600">
                Jobezie is an AI-powered career assistant that provides tools for resume optimization, recruiter relationship management, outreach message generation, labor market analysis, LinkedIn profile optimization, and AI career coaching. The Service uses algorithms and artificial intelligence to generate scores, recommendations, and content.
              </p>
            </section>

            {/* 3. AI Disclaimer */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">3. AI-Generated Content Disclaimer</h2>
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-sm text-blue-800 font-medium">Important: Please read this section carefully.</p>
              </div>
              <p className="text-gray-600 mt-3">
                Jobezie uses artificial intelligence (including Anthropic's Claude and OpenAI's GPT-4) to generate content, scores, and recommendations. You acknowledge and agree that:
              </p>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>AI-generated content, including resume scores, career recommendations, coaching advice, and outreach messages, is <strong>guidance only</strong> and does not constitute professional career advice, employment advice, legal advice, or guaranteed outcomes.</li>
                <li>Algorithmic scores (ATS scoring, career readiness, recruiter fit, etc.) are calculated based on pattern matching and statistical models. They are <strong>not employment decisions</strong> and should not be treated as such.</li>
                <li>You are responsible for reviewing, editing, and verifying all AI-generated content before using it in any professional context.</li>
                <li>Jobezie does not guarantee that using the Service will result in job offers, interviews, or any specific career outcomes.</li>
                <li>AI systems may occasionally produce inaccurate, incomplete, or inappropriate content. Use your own judgment when acting on AI suggestions.</li>
              </ul>
            </section>

            {/* 4. Account Terms */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">4. Account Terms</h2>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>You must be at least 13 years old to use the Service.</li>
                <li>You must provide accurate and complete registration information.</li>
                <li>You are responsible for maintaining the security of your account credentials.</li>
                <li>You may not create more than one account per person.</li>
                <li>You must notify us immediately of any unauthorized use of your account.</li>
              </ul>
            </section>

            {/* 5. Acceptable Use */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">5. Acceptable Use</h2>
              <p className="text-gray-600">You agree not to use the Service to:</p>
              <ul className="list-disc pl-6 text-gray-600 space-y-1">
                <li>Upload content that is illegal, harmful, threatening, abusive, or otherwise objectionable</li>
                <li>Impersonate any person or entity, or misrepresent your identity or qualifications</li>
                <li>Scrape, crawl, or use automated tools to extract data from the Service</li>
                <li>Attempt to access other users' accounts or data</li>
                <li>Interfere with or disrupt the Service or servers</li>
                <li>Use the Service to send spam, unsolicited messages, or harass others</li>
                <li>Reverse engineer, decompile, or disassemble any part of the Service</li>
                <li>Use AI-generated content in a way that is deceptive or misleading</li>
              </ul>
            </section>

            {/* 6. Intellectual Property */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">6. Intellectual Property</h2>
              <h3 className="text-lg font-medium text-gray-800 mt-4">Your Content</h3>
              <p className="text-gray-600">
                You retain ownership of all content you upload to the Service, including resumes, career information, and messages. By uploading content, you grant Jobezie a limited license to process, store, and analyze your content solely to provide the Service.
              </p>
              <h3 className="text-lg font-medium text-gray-800 mt-4">AI-Generated Content</h3>
              <p className="text-gray-600">
                Content generated by our AI features (optimized resumes, messages, coaching responses) is provided for your personal use. You may use AI-generated content in your job search activities.
              </p>
              <h3 className="text-lg font-medium text-gray-800 mt-4">Our Platform</h3>
              <p className="text-gray-600">
                The Service, including its algorithms, design, code, and documentation, is owned by Jobezie and protected by intellectual property laws. You may not copy, modify, or distribute any part of the Service without our written permission.
              </p>
            </section>

            {/* 7. Subscriptions */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">7. Subscriptions and Payments</h2>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>Jobezie offers free (Basic) and paid (Pro, Expert, Career Keeper) subscription tiers.</li>
                <li>Paid subscriptions are billed monthly through Stripe. Prices are displayed on our pricing page.</li>
                <li>You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period.</li>
                <li>We do not offer refunds for partial billing periods, except as required by law.</li>
                <li>We reserve the right to change pricing with 30 days' notice to existing subscribers.</li>
                <li>Feature limits (number of recruiters, resumes, AI messages) are enforced per your subscription tier.</li>
              </ul>
            </section>

            {/* 8. Limitation of Liability */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">8. Limitation of Liability</h2>
              <p className="text-gray-600">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, JOBEZIE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, OR EMPLOYMENT OPPORTUNITIES, ARISING FROM YOUR USE OF THE SERVICE.
              </p>
              <p className="text-gray-600 mt-3">
                OUR TOTAL LIABILITY FOR ANY CLAIMS ARISING FROM THE SERVICE SHALL NOT EXCEED THE AMOUNT YOU PAID TO US IN THE 12 MONTHS PRECEDING THE CLAIM.
              </p>
              <p className="text-gray-600 mt-3">
                The Service is provided "as is" and "as available" without warranties of any kind, whether express or implied, including merchantability, fitness for a particular purpose, and non-infringement.
              </p>
            </section>

            {/* 9. Termination */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">9. Termination</h2>
              <p className="text-gray-600">
                You may delete your account at any time through the Settings page. We may suspend or terminate your account if you violate these Terms or engage in conduct that is harmful to other users or the Service. Upon termination, your right to use the Service ceases immediately. We will delete your data in accordance with our Privacy Policy.
              </p>
            </section>

            {/* 10. Dispute Resolution */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">10. Dispute Resolution</h2>
              <p className="text-gray-600">
                Any disputes arising from these Terms or the Service shall be resolved through good-faith negotiation. If negotiation fails, disputes shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association, conducted in the United States.
              </p>
            </section>

            {/* 11. Governing Law */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">11. Governing Law</h2>
              <p className="text-gray-600">
                These Terms shall be governed by and construed in accordance with the laws of the United States, without regard to conflict of law provisions.
              </p>
            </section>

            {/* 12. Contact */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900">12. Contact Us</h2>
              <p className="text-gray-600">
                If you have questions about these Terms, contact us at:
              </p>
              <p className="text-gray-600 mt-2">
                <strong>Email:</strong> legal@jobezie.com
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
