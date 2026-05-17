import { useState, useEffect, useRef } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { getTransactionMessages, sendTransactionMessage, markMessagesRead } from "@/lib/api";
import { X, Send } from "lucide-react";

function formatTime(isoStr) {
  if (!isoStr) return "";
  const date = new Date(isoStr);
  const now = new Date();
  const diffMs = now - date;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "à l'instant";
  if (diffMin < 60) return `il y a ${diffMin} min`;
  return date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}

export default function TransactionMessaging({
  transactionId,
  open,
  onClose,
  currentUserId,
  otherPartyName,
}) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!open || !transactionId) return;
    let cancelled = false;

    const fetchMessages = () => {
      getTransactionMessages(transactionId)
        .then((r) => { if (!cancelled) setMessages(r.data || []); })
        .catch(() => {});
    };

    setLoading(true);
    getTransactionMessages(transactionId)
      .then((r) => { if (!cancelled) setMessages(r.data || []); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    markMessagesRead(transactionId).catch(() => {});

    const interval = setInterval(fetchMessages, 5000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [open, transactionId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    const content = input.trim();
    if (!content || sending) return;
    setSending(true);
    try {
      const r = await sendTransactionMessage(transactionId, content);
      setMessages((prev) => [...prev, r.data]);
      setInput("");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de l'envoi");
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Sheet open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <SheetContent
        side="right"
        className="bg-background border-border w-full max-w-md flex flex-col p-0"
      >
        <SheetHeader className="px-4 py-3 border-b border-border shrink-0 flex flex-row items-center justify-between">
          <SheetTitle
            className="tracking-tighter text-left"
            style={{ fontFamily: "Barlow Condensed", textTransform: "uppercase" }}
          >
            Messages
            {otherPartyName && (
              <span
                className="ml-2 text-sm font-normal text-muted-foreground"
                style={{ fontFamily: "DM Sans", textTransform: "none" }}
              >
                avec @{otherPartyName}
              </span>
            )}
          </SheetTitle>
          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </SheetHeader>

        {/* Messages list */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-xs text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
                Chargement…
              </p>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-xs text-muted-foreground text-center" style={{ fontFamily: "DM Sans" }}>
                Aucun message pour l'instant.<br />Commencez la conversation.
              </p>
            </div>
          ) : (
            messages.map((msg) => {
              const isMine = msg.sender_id === currentUserId;
              return (
                <div
                  key={msg.message_id}
                  className={`flex ${isMine ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] px-3 py-2 border ${
                      isMine
                        ? "bg-primary/10 border-primary/20"
                        : "bg-card border-border"
                    }`}
                  >
                    <p
                      className="text-sm break-words"
                      style={{ fontFamily: "DM Sans" }}
                    >
                      {msg.content}
                    </p>
                    <p
                      className="text-[10px] text-muted-foreground mt-1"
                      style={{ fontFamily: "Barlow Condensed" }}
                    >
                      {formatTime(msg.created_at)}
                    </p>
                  </div>
                </div>
              );
            })
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="shrink-0 border-t border-border px-4 py-3 flex gap-2 items-end bg-background">
          <Textarea
            ref={textareaRef}
            rows={2}
            placeholder="Votre message…"
            value={input}
            onChange={(e) => setInput(e.target.value.slice(0, 1000))}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none text-sm rounded-none"
            style={{ fontFamily: "DM Sans" }}
            disabled={sending}
          />
          <Button
            size="sm"
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="rounded-none shrink-0 h-[58px]"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
