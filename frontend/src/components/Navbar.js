import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { Search, FolderOpen, User, LogOut, FileCheck, Heart, Shield, Trophy, Tag, Users } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/browse';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 glass-header border-b border-border" data-testid="main-navbar">
      <div className="flex items-center justify-between px-4 lg:px-8 h-16">
        {/* Left - Logo & Nav */}
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2" data-testid="navbar-logo">
            <img src="/topkit-logo.png" alt="Topkit" className="h-6 w-auto invert-0 brightness-200" />
          </Link>
          <div className="hidden md:flex items-center gap-1">
            <Link to="/browse">
              <Button variant="ghost" size="sm" className={`rounded-none text-sm ${isActive('/browse') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`} data-testid="nav-browse">
                <Search className="w-4 h-4 mr-1.5" />
                Browse
              </Button>
            </Link>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className={`rounded-none text-sm ${['/teams', '/leagues', '/brands', '/players'].some(p => isActive(p)) ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`} data-testid="nav-database">
                  Database
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-40 bg-card border-border">
                <DropdownMenuItem onClick={() => navigate('/teams')} className="cursor-pointer" data-testid="nav-teams">
                  <Shield className="w-4 h-4 mr-2" /> Teams
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/leagues')} className="cursor-pointer" data-testid="nav-leagues">
                  <Trophy className="w-4 h-4 mr-2" /> Leagues
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/brands')} className="cursor-pointer" data-testid="nav-brands">
                  <Tag className="w-4 h-4 mr-2" /> Brands
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/players')} className="cursor-pointer" data-testid="nav-players">
                  <Users className="w-4 h-4 mr-2" /> Players
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            {user && (
              <>
                <Link to="/collection">
                  <Button variant="ghost" size="sm" className={`rounded-none text-sm ${isActive('/collection') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`} data-testid="nav-collection">
                    <FolderOpen className="w-4 h-4 mr-1.5" />
                    My Collection
                  </Button>
                </Link>
                <Link to="/wishlist">
                  <Button variant="ghost" size="sm" className={`rounded-none text-sm ${isActive('/wishlist') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`} data-testid="nav-wishlist">
                    <Heart className="w-4 h-4 mr-1.5" />
                    Wishlist
                  </Button>
                </Link>
                <Link to="/contributions">
                  <Button variant="ghost" size="sm" className={`rounded-none text-sm ${isActive('/contributions') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'}`} data-testid="nav-contributions">
                    <FileCheck className="w-4 h-4 mr-1.5" />
                    Contributions
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Right - Auth */}
        <div className="flex items-center gap-3">
          {loading ? null : user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 focus:outline-none" data-testid="user-menu-trigger">
                  <Avatar className="w-8 h-8 border border-border">
                    <AvatarImage src={user.picture} alt={user.name} />
                    <AvatarFallback className="bg-secondary text-xs">{user.name?.[0]}</AvatarFallback>
                  </Avatar>
                  <span className="hidden md:block text-sm text-muted-foreground">{user.name?.split(' ')[0]}</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 bg-card border-border">
                <DropdownMenuItem onClick={() => navigate('/profile')} className="cursor-pointer" data-testid="menu-profile">
                  <User className="w-4 h-4 mr-2" /> Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/collection')} className="cursor-pointer" data-testid="menu-collection">
                  <FolderOpen className="w-4 h-4 mr-2" /> My Collection
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/wishlist')} className="cursor-pointer" data-testid="menu-wishlist">
                  <Heart className="w-4 h-4 mr-2" /> Wishlist
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/contributions')} className="cursor-pointer" data-testid="menu-contributions">
                  <FileCheck className="w-4 h-4 mr-2" /> Contributions
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="cursor-pointer text-destructive" data-testid="menu-logout">
                  <LogOut className="w-4 h-4 mr-2" /> Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button onClick={handleLogin} size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-none" data-testid="navbar-login-btn">
              Sign in
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}
