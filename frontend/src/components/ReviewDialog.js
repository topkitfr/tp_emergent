import { useState } from "react";
import { Star } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { submitReview } from "@/lib/api";

export default function ReviewDialog({ open, onClose, transactionId, otherPartyName, onSuccess }) {
  const [score, setScore] = useState(0);
  const [hovered, setHovered] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (score < 1) {
      toast.error("Veuillez sélectionner une note");
      return;
    }
    setSubmitting(true);
    try {
      await submitReview(transactionId, { score, comment });
      toast.success("Avis envoyé !");
      onSuccess?.();
      onClose?.();
      setScore(0);
      setComment("");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de l'envoi de l'avis");
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onClose?.();
    }
  };

  const displayScore = hovered > 0 ? hovered : score;

  return (
    <Dialog open={open} onOpenChange={open => { if (!open) handleClose(); }}>
      <DialogContent className="max-w-sm rounded-none">
        <DialogHeader>
          <DialogTitle style={{ fontFamily: "Barlow Condensed", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Laisser un avis à @{otherPartyName}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Star rating */}
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: "Barlow Condensed" }}>
              Note
            </p>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setScore(star)}
                  onMouseEnter={() => setHovered(star)}
                  onMouseLeave={() => setHovered(0)}
                  className="focus:outline-none transition-colors"
                  disabled={submitting}
                >
                  <Star
                    className={`w-8 h-8 transition-colors ${
                      star <= displayScore
                        ? "text-yellow-400 fill-yellow-400"
                        : "text-muted-foreground"
                    }`}
                  />
                </button>
              ))}
              {score > 0 && (
                <span className="ml-2 text-sm text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
                  {score}/5
                </span>
              )}
            </div>
          </div>

          {/* Comment */}
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: "Barlow Condensed" }}>
              Commentaire (optionnel)
            </p>
            <Textarea
              value={comment}
              onChange={e => setComment(e.target.value.slice(0, 500))}
              placeholder="Décrivez votre expérience…"
              className="rounded-none min-h-[80px] resize-none"
              style={{ fontFamily: "DM Sans" }}
              disabled={submitting}
              maxLength={500}
            />
            <p className="text-[10px] text-muted-foreground text-right" style={{ fontFamily: "DM Sans" }}>
              {comment.length}/500
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={submitting}
            className="rounded-none"
          >
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || score < 1}
            className="rounded-none"
          >
            {submitting ? "Envoi…" : "Envoyer l'avis"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
