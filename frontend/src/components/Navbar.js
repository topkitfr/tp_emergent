// frontend/src/components/Navbar.js
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
import NotificationBell from '@/components/NotificationBell';

export default function Navbar() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = () => navigate('/login');

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
              <Button
                variant="ghost"
                size="sm"
                className={`rounded-none text-sm ${
                  isActive('/browse') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                }`}
                data-testid="nav-browse"
              >
                <Search className="w-4 h-4 mr-1.5" />
                Browse
              </Button>
            </Link>

            {/* Database dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`rounded-none text-sm ${
                    ['/teams', '/leagues', '/brands', '/players', '/database/sponsors'].some(p => isActive(p))
                      ? 'text-primary'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  data-testid="nav-database"
                >
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
                <DropdownMenuItem
                  onClick={() => navigate('/database/sponsors')}
                  className="cursor-pointer"
                  data-testid="nav-sponsors"
                >
                  <Tag className="w-4 h-4 mr-2" /> Sponsors
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {user && (
              <Link to="/contributions">
                <Button
                  variant="ghost"
                  size="sm"
                  className={`rounded-none text-sm ${
                    isActive('/contributions') ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                  }`}
                  data-testid="nav-contributions"
                >
                  <FileCheck className="w-4 h-4 mr-1.5" />
                  Contributions
                </Button>
              </Link>
            )}
          </div>
        </div>

        {/* Right - Notifications + Auth */}
        <div className="flex items-center gap-3">
          {/* 🔔 Cloche de notifications — visible uniquement si connecté */}
          {!loading && user && <NotificationBell />}

          {loading ? null : user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 focus:outline-none" data-testid="user-menu-trigger">
                  <Avatar className="w-8 h-8 border border-border">
                    <AvatarImage src={user.picture} alt={user.name} />
                    <AvatarFallback className="bg-secondary text-xs">
                      {user.name?.[0]}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 bg-card border-border">
                <div className="px-3 py-2 border-b border-border">
                  <p className="text-sm font-medium text-foreground truncate">{user.name}</p>
                  <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                  {(user.role === 'moderator' || user.role === 'admin') && (
                    <span className="inline-flex items-center mt-1 px-1.5 py-0.5 text-[10px] font-semibold bg-primary/20 text-primary rounded">
                      {user.role === 'admin' ? 'Admin' : 'Modérateur'}
                    </span>
                  )}
                </div>
                <DropdownMenuItem onClick={() => navigate('/collection')} className="cursor-pointer" data-testid="nav-collection">
                  <FolderOpen className="w-4 h-4 mr-2" /> Ma Collection
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/wishlist')} className="cursor-pointer" data-testid="nav-wishlist">
                  <Heart className="w-4 h-4 mr-2" /> Wishlist
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/profile')} className="cursor-pointer" data-testid="nav-profile">
                  <User className="w-4 h-4 mr-2" /> Profil
                </DropdownMenuItem>
                {(user.role === 'moderator' || user.role === 'admin') && (
                  <>
                    <DropdownMenuSeparator className="bg-border" />
                    <DropdownMenuItem onClick={() => navigate('/admin')} className="cursor-pointer text-primary" data-testid="nav-admin">
                      <Shield className="w-4 h-4 mr-2" /> Admin
                    </DropdownMenuItem>
                  </>
                )}
                <DropdownMenuSeparator className="bg-border" />
                <DropdownMenuItem
                  onClick={logout}
                  className="cursor-pointer text-destructive focus:text-destructive"
                  data-testid="nav-logout"
                >
                  <LogOut className="w-4 h-4 mr-2" /> Déconnexion
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button
              size="sm"
              onClick={handleLogin}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="nav-login"
            >
              Se connecter
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}
