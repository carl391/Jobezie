import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Users,
  MessageSquare,
  Sparkles,
  BarChart3,
  ArrowRight,
  Check,
  Star,
  TrendingUp,
  Linkedin,
  ChevronRight,
} from 'lucide-react';

const FEATURES = [
  {
    icon: FileText,
    title: 'ATS Resume Scoring',
    description: 'Get your resume scored across 7 categories used by real ATS systems. Know exactly what to fix before you apply.',
    stat: '75% of resumes never reach human eyes',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: Users,
    title: 'Recruiter CRM',
    description: 'Track every recruiter relationship through an 8-stage pipeline. Never lose track of a conversation again.',
    stat: '70-80% of jobs are in the hidden market',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    icon: MessageSquare,
    title: 'AI Message Generation',
    description: 'Generate personalized outreach messages scored for quality. Under 150 words, with the right tone.',
    stat: '22% higher response rate with optimized messages',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: Sparkles,
    title: 'AI Career Coach',
    description: 'Get personalized career advice powered by your actual scores and data. 4 coaching modes for every situation.',
    stat: 'Personalized to your career stage and goals',
    color: 'bg-amber-100 text-amber-600',
  },
  {
    icon: BarChart3,
    title: 'Labor Market Intelligence',
    description: 'Real-time shortage scores, salary benchmarks, and opportunity analysis powered by O*NET data.',
    stat: '1,016 occupations analyzed',
    color: 'bg-rose-100 text-rose-600',
  },
  {
    icon: Linkedin,
    title: 'LinkedIn Optimizer',
    description: 'Generate optimized headlines, summaries, and experience sections. Maximize your visibility score.',
    stat: '87% of recruiters use LinkedIn as primary source',
    color: 'bg-sky-100 text-sky-600',
  },
];

const TIERS = [
  {
    name: 'Basic',
    slug: 'basic',
    price: 0,
    period: 'Free forever',
    description: 'Get started with essential tools',
    features: ['5 recruiter contacts', '2 resume uploads', 'Basic ATS scoring', '10 AI messages/mo', 'AI Career Coach'],
    cta: 'Start Free',
    popular: false,
    color: 'border-gray-200',
  },
  {
    name: 'Pro',
    slug: 'pro',
    price: 19,
    period: '/month',
    description: 'For serious job seekers',
    features: ['50 recruiter contacts', '10 resume uploads', 'Advanced ATS scoring', '100 AI messages/mo', 'Interview prep', 'Priority support'],
    cta: 'Start Pro',
    popular: true,
    color: 'border-primary-500',
  },
  {
    name: 'Expert',
    slug: 'expert',
    price: 39,
    period: '/month',
    description: 'Maximum career acceleration',
    features: ['Unlimited recruiters', 'Unlimited resumes', 'Full AI coaching', 'Unlimited messages', 'Interview prep', 'Dedicated support'],
    cta: 'Start Expert',
    popular: false,
    color: 'border-gray-200',
  },
  {
    name: 'Career Keeper',
    slug: 'career_keeper',
    price: 9,
    period: '/month',
    description: 'Stay career-ready while employed',
    features: ['5 key recruiter contacts', 'Annual resume refresh', 'Salary monitoring', 'Skills gap alerts', 'Market trend updates'],
    cta: 'Start Keeper',
    popular: false,
    color: 'border-gray-200',
  },
];

const STATS = [
  { value: '94', label: 'API Endpoints' },
  { value: '7', label: 'ATS Score Categories' },
  { value: '6', label: 'Scoring Algorithms' },
  { value: '1,016', label: 'Occupations Analyzed' },
];

export function Landing() {
  // Handle hash scroll for anchor links (e.g. /#features, /#pricing)
  useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
      const el = document.querySelector(hash);
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent tracking-tight">Jobezie</span>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#pricing" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
              <a href="#how-it-works" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">How It Works</a>
            </div>
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="btn btn-primary text-sm flex items-center gap-1"
              >
                Get Started Free <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-purple-50" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 lg:pt-32 lg:pb-36">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 border border-primary-100 text-primary-700 text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4" />
              AI-Powered Career Assistant
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 tracking-tight leading-tight">
              Land your dream job
              <br />
              <span className="bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                with AI precision
              </span>
            </h1>

            <p className="mt-6 text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Jobezie scores your resume, crafts perfect outreach messages, and
              manages your recruiter pipeline — all powered by evidence-based
              algorithms and dual AI.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="btn bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-semibold rounded-xl shadow-lg shadow-primary-500/25 transition-all hover:shadow-xl hover:shadow-primary-500/30 flex items-center gap-2"
              >
                Start Free <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="#features"
                className="btn btn-outline px-8 py-3 text-lg rounded-xl flex items-center gap-2"
              >
                See Features <ChevronRight className="w-5 h-5" />
              </a>
            </div>

            <p className="mt-4 text-sm text-gray-500">
              Free forever on Basic plan. No credit card required.
            </p>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-y border-gray-100 bg-gray-50/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                  {stat.value}
                </p>
                <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Everything you need to land the job
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Six powerful tools backed by recruiting industry research and real data.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="group p-6 rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-lg transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-xl ${feature.color} flex items-center justify-center mb-4`}>
                  <feature.icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed mb-4">
                  {feature.description}
                </p>
                <p className="text-xs text-primary-600 font-medium flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {feature.stat}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Get started in minutes
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Three simple steps to accelerate your career
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '1',
                title: 'Upload your resume',
                description: 'Get an instant ATS score across 7 categories. See exactly what recruiters and algorithms see.',
                icon: FileText,
              },
              {
                step: '2',
                title: 'Add your recruiters',
                description: 'Build your pipeline with an 8-stage CRM. Track engagement, fit scores, and follow-up timing.',
                icon: Users,
              },
              {
                step: '3',
                title: 'Send AI-crafted messages',
                description: 'Generate personalized outreach scored for quality. Under 150 words with proven response patterns.',
                icon: MessageSquare,
              },
            ].map((item) => (
              <div key={item.step} className="relative text-center">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-600 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary-500/25">
                  <item.icon className="w-7 h-7 text-white" />
                </div>
                <div className="absolute top-7 left-1/2 w-full h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent hidden md:block" style={{ transform: 'translateX(50%)' }} />
                <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold mb-3">
                  {item.step}
                </span>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social proof */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Built on real recruiting research
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Every algorithm is grounded in data from 49,000+ outreach attempts, NACE surveys, and BLS labor statistics.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { stat: '40%', label: 'more interviews with quantified achievements' },
              { stat: '22%', label: 'higher response rate with optimized messages' },
              { stat: '75%', label: 'of resumes filtered by ATS before human eyes' },
              { stat: '7.4s', label: 'average time recruiters spend scanning a resume' },
            ].map((item) => (
              <div key={item.stat} className="p-6 rounded-2xl bg-gradient-to-br from-gray-50 to-white border border-gray-100 text-center">
                <p className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                  {item.stat}
                </p>
                <p className="text-sm text-gray-600 mt-2">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Start free. Upgrade when you're ready.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {TIERS.map((tier) => (
              <div
                key={tier.name}
                className={`relative p-6 rounded-2xl bg-white border-2 flex flex-col ${tier.color} ${
                  tier.popular ? 'shadow-xl shadow-primary-500/10' : 'shadow-sm'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-primary-600 to-purple-600 text-white text-xs font-semibold">
                      <Star className="w-3 h-3" /> Most Popular
                    </span>
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">{tier.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{tier.description}</p>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">${tier.price}</span>
                    <span className="text-gray-500 text-sm">{tier.period}</span>
                  </div>
                </div>
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  to={`/register?plan=${tier.slug}`}
                  className={`mt-auto block text-center py-2.5 px-4 rounded-xl font-medium text-sm transition-all ${
                    tier.popular
                      ? 'bg-gradient-to-r from-primary-600 to-purple-600 text-white hover:from-primary-700 hover:to-purple-700 shadow-md'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {tier.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="p-12 rounded-3xl bg-gradient-to-br from-primary-600 to-purple-600 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" />
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Ready to accelerate your career?
              </h2>
              <p className="text-primary-100 text-lg mb-8 max-w-xl mx-auto">
                Join Jobezie today and get your resume scored, messages optimized, and
                career coached — all for free.
              </p>
              <Link
                to="/register"
                className="inline-flex items-center gap-2 px-8 py-3 bg-white text-primary-700 font-semibold rounded-xl hover:bg-primary-50 transition-colors shadow-lg"
              >
                Get Started Free <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-bold text-gray-900">Jobezie</span>
              <span className="text-gray-400 text-sm ml-2">&copy; {new Date().getFullYear()}</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-500">
              <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
              <a href="#pricing" className="hover:text-gray-900 transition-colors">Pricing</a>
              <Link to="/privacy" className="hover:text-gray-900 transition-colors">Privacy</Link>
              <Link to="/terms" className="hover:text-gray-900 transition-colors">Terms</Link>
              <Link to="/login" className="hover:text-gray-900 transition-colors">Sign In</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
