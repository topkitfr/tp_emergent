// src/components/AddToCollectionDialog.jsx
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { proxyImageUrl } from "@/lib/api";
import { Shirt, Loader2 } from "lucide-react";

const SIZES = ["XS", "S", "M", "L", "XL", "XXL", "S/S", "M/S", "L/S", "XL/S", "Youth"];
const CONDITIONS = ["New with tag", "Very good", "Used", "Damaged", "Needs restoration"];
const ORIGINS = ["Shop", "Club Stock", "Training", "Match Prepared", "Match Worn"];
const CATEGORIES = ["General", "Match Worn", "Signed", "Display", "Loan"];

export default function AddToCollectionDialog({ version, onClose, onSuccess }) {
  const kit = version?.master_kit || {};
  const photo = version?.front_photo || kit?.front_photo;

  const [form, setForm] = useState({
    category:         "General",
    size:             "",
    condition_origin: "",
    physical_state:   "",
    notes:            "",
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  const set = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/collections", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          version_id:       version.version_id,
          category:         form.category,
          size:             form.size,
          condition_origin: form.condition_origin,
          physical_state:   form.physical_state,
          notes:            form.notes,
        }),
      });

      if (res.status === 400) {
        setError("This version is already in your collection.");
        setLoading(false);
        return;
      }
      if (!res.ok) {
        setError("An error occurred. Please try again.");
        setLoading(false);
        return;
      }

      onSuccess?.();
    } catch {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="font-semibold tracking-tight"
            style={{ fontFamily: "Barlow Condensed, sans-serif", textTransform: "uppercase", fontSize: "1.1rem" }}
          >
            Add to Collection
          </DialogTitle>
        </DialogHeader>

        {/* Aperçu version */}
        <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
          <div className="w-14 h-14 rounded bg-secondary border flex items-center justify-center overflow-hidden shrink-0">
            {photo ? (
              <img src={proxyImageUrl(photo)} alt={kit.club} className="w-full h-full object-cover" />
            ) : (
              <Shirt className="w-6 h-6 text-muted-foreground" />
            )}
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-sm truncate uppercase"
              style={{ fontFamily: "Barlow Condensed, sans-serif" }}
            >
              {kit.club ?? "—"}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {kit.season} · {version.competition} · {version.model}
            </p>
            {kit.brand && (
              <p className="font-mono text-[10px] text-muted-foreground">{kit.brand}</p>
            )}
          </div>
        </div>

        {/* Formulaire */}
        <div className="space-y-4">

          {/* Catégorie */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground">Category</Label>
            <Select value={form.category} onValueChange={(v) => set("category", v)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Taille + Provenance */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs uppercase tracking-wide text-muted-foreground">Size</Label>
              <Select value={form.size} onValueChange={(v) => set("size", v)}>
                <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                <SelectContent>
                  {SIZES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs uppercase tracking-wide text-muted-foreground">Origin</Label>
              <Select value={form.condition_origin} onValueChange={(v) => set("condition_origin", v)}>
                <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                <SelectContent>
                  {ORIGINS.map((o) => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* État physique */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground">Condition</Label>
            <Select value={form.physical_state} onValueChange={(v) => set("physical_state", v)}>
              <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
              <SelectContent>
                {CONDITIONS.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Notes */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground">Notes</Label>
            <Textarea
              placeholder="Optional notes..."
              value={form.notes}
              onChange={(e) => set("notes", e.target.value)}
              rows={2}
              className="resize-none text-sm"
            />
          </div>

          {/* Erreur */}
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading
              ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Adding...</>
              : "Add to collection"
            }
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
