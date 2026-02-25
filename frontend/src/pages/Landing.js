import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { getStats, seedData } from '@/lib/api';
import { Shirt, Search, Star, Users, Database, ArrowRight } from 'lucide-react';
import LatestAdditionsSection from '@/components/ui/LatestAdditionsSection';


export default function Landing() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ master_kits: 0, versions: 0, users: 0, reviews: 0 });

  useEffect(() => {
    const init = async () => {
      try {
        await seedData();
      } catch { /* already seeded */ }
      try {
        const res = await getStats();
        setStats(res.data);
      } catch { /* ignore */ }
    };
    init();
  }, []);

  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/browse';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Stadium glow effect */}
      <div className="absolute inset-0 stadium-glow pointer-events-none" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 lg:px-12 py-5">
        <Link to="/" className="flex items-center gap-2" data-testid="landing-logo">
          <img src="/topkit-logo.png" alt="Topkit" className="h-7 object-contain" style={{ aspectRatio: 'auto' }} />
        </Link>
        <div className="flex items-center gap-4">
          {loading ? null : user ? null : (
            <Button onClick={handleLogin} className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-none" data-testid="login-btn">
              Sign in with Google
            </Button>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 px-6 lg:px-12 pt-20 pb-32 lg:pt-32 lg:pb-44">
        <div className="max-w-5xl">
          <div className="inline-block mb-6 px-3 py-1 border border-primary/30 text-primary text-xs font-mono tracking-wider">
            THE FOOTBALL JERSEY DATABASE
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-8xl leading-none tracking-tighter mb-8" data-testid="hero-title">
            CATALOG.<br />
            <span className="text-primary">COLLECT.</span><br />
            CONNECT.
          </h1>
          <p className="text-lg text-muted-foreground max-w-xl mb-12 font-normal" style={{ textTransform: 'none', fontFamily: 'DM Sans, sans-serif' }}>
            The definitive database for football jersey collectors. Browse, catalog, and share your collection with the community.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link to="/browse">
              <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-none text-base px-8 h-12" data-testid="explore-catalog-btn">
                Explore Catalog
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            {!user && !loading && (
              <Button size="lg" variant="outline" onClick={handleLogin} className="rounded-none text-base px-8 h-12 border-border hover:bg-secondary" data-testid="join-community-btn">
                Join the Community
              </Button>
            )}
          </div>
        </div>
      </section>

      {/* Latest additions */}
      <section className="relative z-10 px-6 lg:px-12 py-16 border-t border-border">
        <div className="max-w-7xl mx-auto">
          <LatestAdditionsSection />
        </div>
      </section>


      {/* Stats */}
      <section className="relative z-10 border-t border-border">
        <div className="grid grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Database, label: 'Master Kits', value: stats.master_kits },
            { icon: Shirt, label: 'Versions', value: stats.versions },
            { icon: Users, label: 'Collectors', value: stats.users },
            { icon: Star, label: 'Reviews', value: stats.reviews },
          ].map((stat, i) => (
            <div key={i} className="px-6 lg:px-12 py-10 border-r border-border last:border-r-0" data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}>
              <stat.icon className="w-5 h-5 text-primary mb-3" />
              <div className="text-3xl lg:text-4xl font-bold tracking-tight mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 px-6 lg:px-12 py-24">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-lg md:text-xl mb-12 text-muted-foreground">
            BUILT FOR COLLECTORS
          </h2>
          <div className="grid md:grid-cols-3 gap-8 stagger-children">
            {[
              {
                icon: Search,
                title: 'BROWSE & DISCOVER',
                desc: 'Search through our extensive database of football jerseys. Filter by club, season, brand, and type.'
              },
              {
                icon: Shirt,
                title: 'CATALOG YOUR KITS',
                desc: 'Add jerseys to your personal collection. Track versions, conditions, and organize with custom categories.'
              },
              {
                icon: Star,
                title: 'RATE & REVIEW',
                desc: 'Share your opinion on jerseys. Rate them on a 5-star scale and help the community discover the best kits.'
              },
            ].map((feat, i) => (
              <div key={i} className="p-8 border border-border bg-card hover:border-primary/30 group" data-testid={`feature-card-${i}`}>
                <feat.icon className="w-6 h-6 text-primary mb-6 group-hover:scale-110" style={{ transition: 'transform 0.3s ease' }} />
                <h3 className="text-xl mb-3 tracking-tight">{feat.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed" style={{ textTransform: 'none', fontFamily: 'DM Sans, sans-serif', fontWeight: 400 }}>
                  {feat.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border px-6 lg:px-12 py-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <img src="/topkit-logo.png" alt="Topkit" className="h-4 object-contain opacity-60" style={{ aspectRatio: 'auto' }} />
          </div>
          <p className="text-xs text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans, sans-serif' }}>
            The football jersey database
          </p>
        </div>
      </footer>
    </div>
  );
}
