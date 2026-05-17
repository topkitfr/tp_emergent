import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { markShipped, confirmReceipt, approveTransaction, openDispute, proxyImageUrl } from "@/lib/api";
import { Package, Truck, CheckCircle, XCircle, AlertTriangle, ArrowRight, Clock, MessageCircle } from "lucide-react";

const STATUS_LABELS = {
  awaiting_shipment: { label: "En attente d'envoi", color: "bg-amber-100 text-amber-800" },
  shipped:           { label: "Envoyé",              color: "bg-blue-100 text-blue-800" },
  delivered:         { label: "Reçu",                color: "bg-purple-100 text-purple-800" },
  completed:         { label: "Finalisé",            color: "bg-green-100 text-green-800" },
  disputed:          { label: "Litige",              color: "bg-red-100 text-red-800" },
};

const STEPS_SALE  = ["Acceptée", "Envoyé", "Reçu", "Approuvé"];
const STEPS_TRADE = ["Acceptée", "Envois", "Réceptions", "Approuvés"];

function StepBar({ txn, isTrade }) {
  const steps = isTrade ? STEPS_TRADE : STEPS_SALE;
  const current =
    txn.status === "completed" ? 4 :
    txn.status === "delivered" ? 3 :
    txn.status === "shipped"   ? 2 : 1;

  return (
    <div className="flex items-center gap-1 mt-3 mb-2">
      {steps.map((s, i) => (
        <div key={s} className="flex items-center gap-1 flex-1">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
            i < current ? "bg-primary text-primary-foreground" :
            i === current - 1 ? "bg-primary/20 text-primary border border-primary" :
            "bg-muted text-muted-foreground"
          }`}>{i < current ? "✓" : i + 1}</div>
          <span className={`text-[10px] hidden sm:block ${i < current ? "text-primary" : "text-muted-foreground"}`}
            style={{ fontFamily: "Barlow Condensed" }}>{s}</span>
          {i < steps.length - 1 && <div className={`h-px flex-1 ${i < current - 1 ? "bg-primary" : "bg-border"}`} />}
        </div>
      ))}
    </div>
  );
}

export default function TransactionCard({ txn, currentUserId, onRefresh, unreadCount = 0, onOpenMessages }) {
  const [loading, setLoading] = useState(false);
  const [tracking, setTracking] = useState("");
  const [showDispute, setShowDispute] = useState(false);
  const [disputeReason, setDisputeReason] = useState("");

  const isSeller = txn.seller_id === currentUserId;
  const isTrade  = txn.transaction_type === "trade";
  const kit      = txn.kit_snapshot || {};
  const counterpart = isSeller ? txn.buyer : txn.seller;
  const statusInfo = STATUS_LABELS[txn.status] || { label: txn.status, color: "bg-muted text-muted-foreground" };

  async function act(fn, successMsg) {
    setLoading(true);
    try {
      await fn();
      toast.success(successMsg);
      onRefresh?.();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur");
    } finally {
      setLoading(false);
    }
  }

  const canShip = isSeller
    ? txn.status === "awaiting_shipment" && !txn.seller_shipped
    : isTrade && txn.status === "awaiting_shipment" && !txn.buyer_shipped;

  const canConfirmReceipt = !isSeller
    ? txn.status === "shipped" && !txn.buyer_received
    : isTrade && txn.status === "shipped" && !txn.seller_received;

  const canApprove = !isSeller
    ? txn.status === "delivered" && !txn.buyer_approved
    : isTrade && txn.status === "delivered" && !txn.seller_approved;

  const canDispute = !["completed", "disputed"].includes(txn.status);

  return (
    <div className={`border bg-card p-4 space-y-3 ${txn.status === "disputed" ? "border-destructive/50" : "border-border"}`}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="w-14 h-18 shrink-0 bg-secondary overflow-hidden border border-border">
          <img
            src={proxyImageUrl(kit.front_photo)}
            alt=""
            className="w-full h-full object-cover"
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-sm font-semibold truncate" style={{ fontFamily: "Barlow Condensed", textTransform: "uppercase" }}>
                {kit.club} — {kit.season}
              </p>
              <p className="text-xs text-muted-foreground">{kit.brand} · {kit.kit_type}</p>
            </div>
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded shrink-0 ${statusInfo.color}`}>
              {statusInfo.label}
            </span>
          </div>
          <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
            <span>{isSeller ? "Acheteur" : "Vendeur"} :</span>
            <span className="font-medium text-foreground">@{counterpart?.username || "?"}</span>
            {txn.agreed_price && <span className="ml-2 font-mono text-accent">{txn.agreed_price} €</span>}
            {isTrade && <Badge variant="outline" className="ml-2 text-[9px] rounded-none">ÉCHANGE</Badge>}
          </div>
        </div>
      </div>

      {/* Progress */}
      {txn.status !== "disputed" && <StepBar txn={txn} isTrade={isTrade} />}

      {/* Trade shipment status */}
      {isTrade && txn.status === "awaiting_shipment" && (
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div className={`flex items-center gap-1 px-2 py-1 border ${txn.seller_shipped ? "border-primary/30 text-primary" : "border-border text-muted-foreground"}`}>
            <Truck className="w-3 h-3" /> Vendeur : {txn.seller_shipped ? "Envoyé ✓" : "En attente"}
          </div>
          <div className={`flex items-center gap-1 px-2 py-1 border ${txn.buyer_shipped ? "border-primary/30 text-primary" : "border-border text-muted-foreground"}`}>
            <Truck className="w-3 h-3" /> Acheteur : {txn.buyer_shipped ? "Envoyé ✓" : "En attente"}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-1">
        {onOpenMessages && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onOpenMessages(txn)}
            className="rounded-none relative"
          >
            <MessageCircle className="w-3 h-3 mr-1" />
            Messages
            {unreadCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-destructive text-destructive-foreground text-[9px] font-bold min-w-[16px] h-4 flex items-center justify-center rounded-full px-1">
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </Button>
        )}
        {canShip && (
          <div className="flex gap-2 w-full">
            <Input
              placeholder="N° de suivi (optionnel)"
              value={tracking}
              onChange={e => setTracking(e.target.value)}
              className="h-8 text-xs"
            />
            <Button size="sm" disabled={loading} onClick={() => act(() => markShipped(txn.transaction_id, tracking), "Envoi confirmé !")} className="shrink-0 rounded-none">
              <Truck className="w-3 h-3 mr-1" /> Marquer envoyé
            </Button>
          </div>
        )}
        {canConfirmReceipt && (
          <Button size="sm" disabled={loading} onClick={() => act(() => confirmReceipt(txn.transaction_id), "Réception confirmée !")} className="rounded-none">
            <Package className="w-3 h-3 mr-1" /> Confirmer réception
          </Button>
        )}
        {canApprove && (
          <Button size="sm" disabled={loading} onClick={() => act(() => approveTransaction(txn.transaction_id), "Maillot approuvé ! Transaction finalisée.")} className="rounded-none bg-green-600 hover:bg-green-700 text-white">
            <CheckCircle className="w-3 h-3 mr-1" /> Approuver le maillot
          </Button>
        )}
        {canDispute && !showDispute && (
          <Button size="sm" variant="ghost" onClick={() => setShowDispute(true)} className="rounded-none text-destructive hover:text-destructive text-xs">
            <AlertTriangle className="w-3 h-3 mr-1" /> Signaler un problème
          </Button>
        )}
      </div>

      {/* Dispute form */}
      {showDispute && (
        <div className="space-y-2 border border-destructive/30 p-3">
          <Textarea
            placeholder="Décrivez le problème..."
            value={disputeReason}
            onChange={e => setDisputeReason(e.target.value)}
            className="text-xs min-h-[60px]"
          />
          <div className="flex gap-2">
            <Button size="sm" variant="destructive" disabled={loading || !disputeReason.trim()} className="rounded-none"
              onClick={() => act(() => openDispute(txn.transaction_id, disputeReason), "Litige ouvert — un modérateur va intervenir.")}>
              Confirmer le litige
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setShowDispute(false)} className="rounded-none">Annuler</Button>
          </div>
        </div>
      )}

      {/* Dispute message */}
      {txn.status === "disputed" && (
        <div className="flex items-start gap-2 p-3 bg-destructive/5 border border-destructive/20 text-xs text-destructive">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Litige en cours</p>
            {txn.dispute_reason && <p className="text-muted-foreground mt-0.5">{txn.dispute_reason}</p>}
          </div>
        </div>
      )}

      {/* Completed */}
      {txn.status === "completed" && (
        <div className="flex items-center gap-2 text-xs text-green-700 bg-green-50 border border-green-200 p-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          Transaction finalisée — le maillot a été transféré.
        </div>
      )}
    </div>
  );
}
