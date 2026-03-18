// frontend/src/components/NotificationBell.js
import React, { useState } from 'react';
import { Bell, Check, CheckCheck, Trash2, X } from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationContext';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

// Icônes selon le type
const NOTIF_ICONS = {
  submission_approved: '✅',
  submission_rejected: '❌',
  report_approved: '✅',
  report_rejected: '❌',
};

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return 'à l\'instant';
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours}h`;
  const days = Math.floor(hours / 24);
  return `il y a ${days}j`;
}

export default function NotificationBell() {
  const { notifications, unreadCount, loading, markAsRead, markAllRead, deleteNotification } = useNotifications();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleNotifClick = async (notif) => {
    if (!notif.read) await markAsRead(notif.notification_id);

    // Navigation contextuelle
    if (notif.submission_id) {
      navigate('/contributions');
    } else if (notif.target_type === 'master_kit' && notif.target_id) {
      navigate(`/kit/${notif.target_id}`);
    }
    setOpen(false);
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <button
          className="relative flex items-center justify-center w-8 h-8 rounded-full hover:bg-secondary/50 transition-colors focus:outline-none"
          aria-label="Notifications"
          data-testid="notification-bell"
        >
          <Bell className="w-4 h-4 text-muted-foreground" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-4 h-4 text-[10px] font-bold bg-primary text-primary-foreground rounded-full">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-80 p-0 bg-card border-border shadow-xl"
        sideOffset={8}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">Notifications</span>
            {unreadCount > 0 && (
              <Badge variant="secondary" className="text-xs px-1.5 py-0 h-4 bg-primary/20 text-primary">
                {unreadCount}
              </Badge>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors"
              title="Tout marquer comme lu"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              Tout lire
            </button>
          )}
        </div>

        {/* Liste */}
        <ScrollArea className="h-[320px]">
          {loading && notifications.length === 0 ? (
            <div className="flex items-center justify-center h-20 text-sm text-muted-foreground">
              Chargement…
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-24 gap-2 text-muted-foreground">
              <Bell className="w-6 h-6 opacity-30" />
              <p className="text-xs">Aucune notification</p>
            </div>
          ) : (
            <div className="divide-y divide-border/50">
              {notifications.map((notif) => (
                <div
                  key={notif.notification_id}
                  className={`relative flex gap-3 px-4 py-3 cursor-pointer transition-colors hover:bg-secondary/30 ${
                    !notif.read ? 'bg-primary/5' : ''
                  }`}
                  onClick={() => handleNotifClick(notif)}
                >
                  {/* Indicateur non-lu */}
                  {!notif.read && (
                    <span className="absolute left-2 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary" />
                  )}

                  {/* Icône type */}
                  <span className="text-base mt-0.5 select-none">
                    {NOTIF_ICONS[notif.type] || '🔔'}
                  </span>

                  {/* Contenu */}
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-semibold leading-tight ${!notif.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {notif.title}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-tight line-clamp-2">
                      {notif.message}
                    </p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">
                      {timeAgo(notif.created_at)}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-1 shrink-0">
                    {!notif.read && (
                      <button
                        onClick={(e) => { e.stopPropagation(); markAsRead(notif.notification_id); }}
                        className="p-0.5 rounded hover:bg-secondary/50 text-muted-foreground hover:text-primary transition-colors"
                        title="Marquer comme lu"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteNotification(notif.notification_id); }}
                      className="p-0.5 rounded hover:bg-secondary/50 text-muted-foreground hover:text-destructive transition-colors"
                      title="Supprimer"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="border-t border-border px-4 py-2">
            <button
              onClick={() => { navigate('/contributions'); setOpen(false); }}
              className="text-xs text-primary hover:underline"
            >
              Voir mes contributions →
            </button>
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
