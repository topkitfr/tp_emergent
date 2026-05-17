import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  getSubmissions, getReports, voteOnSubmission, voteOnReport,
  createSubmission, getMasterKits, proxyImageUrl,
  createTeamPending, createBrandPending, createLeaguePending, createSponsorPending,
  getUserByUsername,
} from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Shirt, AlertTriangle, Plus, Check, Clock, X,
  ArrowLeft, ArrowRight, Activity, Users, Package, Trophy,
  FileCheck, ChevronDown, ChevronUp,
} from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import {
  KIT_TYPES, MODELS, GENDERS, COMPETITIONS, SEASONS,
  getSubmissionTitle, timeAgo,
  FeedCard, ContributorCard, SubmissionDetail, ReportDetail,
  UseExistingKitPanel, VoteCard,
  TYPE_LABELS, TYPE_COLORS, UserLink,
  VOTE_THRESHOLD,
} from '@/components/ContributionComponents';

// ─── helpers ─────────────────────────────────────────────────────────────────

function statusBadgeClass(status) {
  if (status === 'approved') return 'bg-primary/20 text-primary border-primary/30';
  if (status === 'rejected') return 'bg-destructive/20 text-destructive border-destructive/30';
  return 'bg-accent/20 text-accent border-accent/30';
}

// ===== COMPOSANT PRINCIPAL ===================================================

export default function Contributions() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const mainTab = searchParams.get('tab') || 'voter';
  const subTab  = searchParams.get('sub') || 'kits';

  const setMainTab = (tab) => setSearchParams({ tab });
  const setSubTab  = (sub) => setSearchParams({ tab: mainTab, sub });

  // ── voter tab state ────────────────────────────────────────────────────────
  const [submissions, setSubmissions]           = useState([]);
  const [reports, setReports]                   = useState([]);
  const [loadingVoter, setLoadingVoter]         = useState(false);
  const [expandedId, setExpandedId]             = useState(null);

  // ── form (soumettre tab) state ─────────────────────────────────────────────
  const [existingKits, setExistingKits]         = useState([]);
  const [addStep, setAddStep]                   = useState(1);
  const [subType, setSubType]                   = useState('master_kit');
  const [submitting, setSubmitting]             = useState(false);

  const [club, setClub]                         = useState('');
  const [teamId, setTeamId]                     = useState('');
  const [teamIsNational, setTeamIsNational]     = useState(false);
  const [season, setSeason]                     = useState('');
  const [kitType, setKitType]                   = useState('');
  const [brand, setBrand]                       = useState('');
  const [brandId, setBrandId]                   = useState('');
  const [frontPhoto, setFrontPhoto]             = useState('');
  const [design, setDesign]                     = useState('');
  const [sponsor, setSponsor]                   = useState('');
  const [sponsorId, setSponsorId]               = useState('');
  const [leagueId, setLeagueId]                 = useState('');
  const [league, setLeague]                     = useState('');
  const [gender, setGender]                     = useState('');

  const [selectedKit, setSelectedKit]           = useState('');
  const [selectedKitLabel, setSelectedKitLabel] = useState('');
  const [competition, setCompetition]           = useState('');
  const [model, setModel]                       = useState('');
  const [skuCode, setSkuCode]                   = useState('');
  const [eanCode, setEanCode]                   = useState('');
  const [verFrontPhoto, setVerFrontPhoto]       = useState('');
  const [verBackPhoto, setVerBackPhoto]         = useState('');

  // ── my contributions (soumettre tab) ──────────────────────────────────────
  const [myContributions, setMyContributions]   = useState([]);
  const [loadingMine, setLoadingMine]           = useState(false);
  const [mineLoaded, setMineLoaded]             = useState(false);

  // ── historique tab state ───────────────────────────────────────────────────
  const [recentApproved, setRecentApproved]     = useState([]);
  const [topContributors, setTopContributors]   = useState([]);
  const [loadingFeed, setLoadingFeed]           = useState(false);
  const [feedLoaded, setFeedLoaded]             = useState(false);

  // ── computed ───────────────────────────────────────────────────────────────
  const isModerator = user?.role === 'moderator' || user?.role === 'admin';
  const hasVoted = (item) => item.voters?.includes(user?.user_id);

  // categorise pending submissions
  const kitSubs = submissions.filter(s =>
    ['master_kit', 'version'].includes(s.submission_type)
  );
  const entityNewSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    s.data?.mode !== 'edit' && s.data?.mode !== 'removal' &&
    !s.data?.parent_submission_id
  );
  const entityEditSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    ['edit', 'removal'].includes(s.data?.mode)
  );
  const correctionItems = [...reports, ...entityEditSubs];

  const pendingCount = submissions.filter(s => s.status === 'pending').length
    + reports.filter(r => r.status === 'pending').length;

  // ── fetch voter data ───────────────────────────────────────────────────────
  const fetchVoterData = useCallback(async () => {
    setLoadingVoter(true);
    try {
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status: 'pending' }),
        getReports({ status: 'pending' }),
      ]);
      setSubmissions(subsRes.data || []);
      setReports(repsRes.data || []);
    } catch {
      toast.error('Erreur lors du chargement des soumissions');
    } finally {
      setLoadingVoter(false);
    }
  }, []);

  // fetch on mount and whenever voter tab is active
  useEffect(() => {
    if (mainTab === 'voter') {
      fetchVoterData();
    }
  }, [mainTab, fetchVoterData]);

  // fetch master kits for form (always)
  useEffect(() => {
    getMasterKits({ limit: 500 })
      .then(res => setExistingKits(res.data?.results ?? []))
      .catch(console.error);
  }, []);

  // ── fetch historique (lazy) ────────────────────────────────────────────────
  const fetchHistorique = useCallback(async () => {
    if (feedLoaded) return;
    setLoadingFeed(true);
    try {
      const res = await getSubmissions({ status: 'approved', limit: 30 });
      const approved = res.data || [];
      setRecentApproved(approved);

      const counts = {};
      approved.forEach(sub => {
        const key = sub.submitter_username || sub.submitter_name || 'anonymous';
        if (!counts[key]) {
          counts[key] = {
            username: sub.submitter_username,
            name: sub.submitter_name,
            count: 0,
            photo_url: null,
          };
        }
        counts[key].count++;
      });

      const sorted = Object.values(counts).sort((a, b) => b.count - a.count).slice(0, 9);

      const enriched = await Promise.all(
        sorted.map(async (c) => {
          if (!c.username) return c;
          try {
            const profileRes = await getUserByUsername(c.username);
            const profile = profileRes?.data;
            return { ...c, photo_url: profile?.photo_url || null, name: profile?.name || c.name };
          } catch {
            return c;
          }
        })
      );

      setTopContributors(enriched);
      setFeedLoaded(true);
    } catch {
      toast.error('Erreur lors du chargement de l\'historique');
    } finally {
      setLoadingFeed(false);
    }
  }, [feedLoaded]);

  useEffect(() => {
    if (mainTab === 'historique') {
      fetchHistorique();
    }
  }, [mainTab, fetchHistorique]);

  // ── fetch my contributions (lazy) ─────────────────────────────────────────
  const fetchMyContributions = useCallback(async () => {
    if (!user || mineLoaded) return;
    setLoadingMine(true);
    try {
      const [pendingRes, approvedRes, rejectedRes] = await Promise.all([
        getSubmissions({ status: 'pending' }),
        getSubmissions({ status: 'approved', limit: 50 }),
        getSubmissions({ status: 'rejected', limit: 20 }),
      ]);
      const all = [
        ...(pendingRes.data || []),
        ...(approvedRes.data || []),
        ...(rejectedRes.data || []),
      ].filter(sub => sub.submitter_username === user?.username);
      setMyContributions(all);
      setMineLoaded(true);
    } catch {
      toast.error('Erreur lors du chargement de vos contributions');
    } finally {
      setLoadingMine(false);
    }
  }, [user, mineLoaded]);

  useEffect(() => {
    if (mainTab === 'soumettre') {
      fetchMyContributions();
    }
  }, [mainTab, fetchMyContributions]);

  // ── vote handlers ──────────────────────────────────────────────────────────
  const handleVoteSubmission = async (submissionId, isUpvote) => {
    try {
      await voteOnSubmission(submissionId, isUpvote ? 'up' : 'down');
      await fetchVoterData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Impossible d\'enregistrer le vote');
    }
  };

  const handleVoteReport = async (reportId, isUpvote) => {
    try {
      await voteOnReport(reportId, isUpvote ? 'up' : 'down');
      await fetchVoterData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Impossible d\'enregistrer le vote');
    }
  };

  const toggleExpanded = (id) => setExpandedId(prev => (prev === id ? null : id));

  // ── form handlers ──────────────────────────────────────────────────────────
  const closeAddForm = () => {
    setAddStep(1); setSubType('master_kit');
    setClub(''); setTeamId(''); setTeamIsNational(false); setSponsorId(''); setSeason('');
    setKitType(''); setBrand(''); setBrandId(''); setFrontPhoto(''); setDesign('');
    setSponsor(''); setLeague(''); setLeagueId(''); setGender('');
    setSelectedKit(''); setSelectedKitLabel(''); setCompetition(''); setModel('');
    setSkuCode(''); setEanCode(''); setVerFrontPhoto(''); setVerBackPhoto('');
  };

  const handleSelectExistingKit = (kit) => {
    setSelectedKit(kit.kit_id);
    setSelectedKitLabel(`${kit.club} — ${kit.season} (${kit.kit_type})`);
    setAddStep(2); setSubType('version');
  };

  const handleSubmitKit = async () => {
    if (!club.trim() || !season.trim() || !kitType || !brand.trim() || !frontPhoto) {
      toast.error('Please fill all required fields (Club, Season, Type, Brand, Photo)'); return;
    }
    setSubmitting(true);
    try {
      const effSponsor   = teamIsNational ? '' : sponsor;
      const effSponsorId = teamIsNational ? '' : sponsorId;
      const data = {
        club, team_id: teamId, season, kit_type: kitType, brand, brand_id: brandId,
        league, league_id: leagueId, sponsor: effSponsor, sponsor_id: effSponsorId,
        design, gender, front_photo: frontPhoto,
      };
      const submissionRes = await createSubmission({ submission_type: 'master_kit', data });
      const masterKitSubmissionId = submissionRes?.data?.submission_id;
      if (masterKitSubmissionId) {
        const pendingJobs = [];
        if (!teamId    && club.trim())          pendingJobs.push(createTeamPending(   { name: club.trim()    }, masterKitSubmissionId));
        if (!brandId   && brand.trim())         pendingJobs.push(createBrandPending(  { name: brand.trim()   }, masterKitSubmissionId));
        if (!leagueId  && league.trim())        pendingJobs.push(createLeaguePending( { name: league.trim()  }, masterKitSubmissionId));
        if (!effSponsorId && effSponsor.trim()) pendingJobs.push(createSponsorPending({ name: effSponsor.trim() }, masterKitSubmissionId));
        await Promise.allSettled(pendingJobs);
      }
      toast.success('Master kit soumis pour validation communautaire !');
      closeAddForm();
      setMineLoaded(false);
      const kitsRes = await getMasterKits();
      setExistingKits(kitsRes.data?.results ?? []);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitVersion = async () => {
    if (!selectedKit || !competition || !model) {
      toast.error('Please fill all required fields (Parent Kit, Competition, Model)'); return;
    }
    setSubmitting(true);
    try {
      await createSubmission({
        submission_type: 'version',
        data: { kit_id: selectedKit, competition, model, sku_code: skuCode, ean_code: eanCode, front_photo: verFrontPhoto, back_photo: verBackPhoto },
      });
      toast.success('Version soumise pour validation communautaire !');
      closeAddForm();
      setMineLoaded(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  // ─── render helpers ────────────────────────────────────────────────────────

  function renderVoteCard(item, isReport = false) {
    const id = isReport ? item.report_id : item.submission_id;
    const title = isReport
      ? (item.notes || 'Correction soumise')
      : getSubmissionTitle(item, existingKits);
    const subtitle = isReport
      ? <>par <UserLink name={item.reporter_name} username={item.reporter_username} /> — {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</>
      : <>par <UserLink name={item.submitter_name} username={item.submitter_username} /> — {timeAgo(item.created_at)}</>;

    const badges = isReport ? (
      <>
        <Badge variant="outline" className="rounded-none text-[10px]">
          {item.report_type === 'removal' ? 'Demande de suppression' : item.target_type === 'master_kit' ? 'Correction kit' : 'Correction version'}
        </Badge>
      </>
    ) : (
      <>
        <Badge variant="outline" className={`rounded-none text-[10px] border ${TYPE_COLORS[item.submission_type] || ''}`}>
          {TYPE_LABELS[item.submission_type] || item.submission_type}
        </Badge>
        {item.data?.mode === 'removal' && (
          <Badge variant="outline" className="rounded-none text-[10px] border-destructive/50 text-destructive">Suppression</Badge>
        )}
        {item.data?.mode === 'edit' && (
          <Badge variant="outline" className="rounded-none text-[10px] border-orange-500/50 text-orange-500">Édition</Badge>
        )}
      </>
    );

    return (
      <VoteCard
        key={id}
        item={item}
        onVoteUp={() => isReport ? handleVoteReport(id, true) : handleVoteSubmission(id, true)}
        onVoteDown={() => isReport ? handleVoteReport(id, false) : handleVoteSubmission(id, false)}
        hasVoted={hasVoted(item)}
        canVote={true}
        expanded={expandedId === id}
        onToggle={() => toggleExpanded(id)}
        title={title}
        subtitle={subtitle}
        badges={badges}
        isModerator={isModerator}
      >
        {isReport
          ? <ReportDetail rep={item} />
          : <SubmissionDetail sub={item} existingKits={existingKits} />
        }
      </VoteCard>
    );
  }

  function renderEmptyVoterState(label) {
    return (
      <div className="text-center py-12 border border-dashed border-border">
        <FileCheck className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          {label}
        </p>
      </div>
    );
  }

  // ─── render ────────────────────────────────────────────────────────────────

  return (
    <div className="animate-fade-in-up">

      {/* ── HEADER ─────────────────────────────────────────────────────────── */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" style={{ fontFamily: 'Barlow Condensed' }}>CONTRIBUTIONS</h1>
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                Votez sur les soumissions en attente, ajoutez de nouveaux maillots, et découvrez les meilleurs contributeurs.
                {isModerator
                  ? ' En tant que modérateur, votre vote valide instantanément.'
                  : ` ${VOTE_THRESHOLD} votes requis pour validation.`}
              </p>
              {isModerator && (
                <Badge className="mt-2 rounded-none bg-primary/20 text-primary border-primary/30">Moderator</Badge>
              )}
            </div>
            <Button
              onClick={() => setMainTab('soumettre')}
              className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0"
            >
              <Plus className="w-4 h-4 mr-1" /> Add Jersey
            </Button>
          </div>

          <div className="flex items-center gap-6 mt-6 pt-6 border-t border-border flex-wrap">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{pendingCount}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>en attente de vote</span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{topContributors.length || '—'}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>contributeurs actifs</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── MAIN TAB BAR ───────────────────────────────────────────────────── */}
      <div className="border-b border-border px-4 lg:px-8">
        <div className="max-w-5xl mx-auto flex items-center gap-0">
          {[
            { key: 'voter', label: 'À voter', icon: <Clock className="w-3.5 h-3.5 mr-1.5" /> },
            { key: 'soumettre', label: 'Soumettre', icon: <Plus className="w-3.5 h-3.5 mr-1.5" /> },
            { key: 'historique', label: 'Historique', icon: <Activity className="w-3.5 h-3.5 mr-1.5" /> },
          ].map(({ key, label, icon }) => (
            <button
              key={key}
              onClick={() => setMainTab(key)}
              className={`flex items-center px-4 py-3 text-xs uppercase tracking-wider border-b-2 transition-colors ${
                mainTab === key
                  ? 'border-primary text-primary font-semibold'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
              style={{ fontFamily: 'Barlow Condensed' }}
            >
              {icon}{label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8">

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* TAB: À VOTER                                                       */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {mainTab === 'voter' && (
          <div>
            {/* Sub-tab bar */}
            <div className="flex items-center gap-0 mb-6 border-b border-border">
              {[
                { key: 'kits', label: 'Kits & Versions', count: kitSubs.length },
                { key: 'refs', label: 'Références', count: entityNewSubs.length },
                { key: 'corrections', label: 'Corrections', count: correctionItems.length },
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setSubTab(key)}
                  className={`flex items-center gap-1.5 px-3 py-2 text-[11px] uppercase tracking-wider border-b-2 transition-colors ${
                    subTab === key
                      ? 'border-primary text-primary font-semibold'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  }`}
                  style={{ fontFamily: 'Barlow Condensed' }}
                >
                  {label}
                  {count > 0 && (
                    <span className={`font-mono text-[9px] px-1 ${subTab === key ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                      {count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {loadingVoter ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-card animate-pulse border border-border" />
                ))}
              </div>
            ) : (
              <>
                {/* Sub-tab: Kits & Versions */}
                {subTab === 'kits' && (
                  <div className="space-y-3">
                    {kitSubs.length === 0
                      ? renderEmptyVoterState('Aucun kit ou version en attente de vote')
                      : kitSubs.map(sub => renderVoteCard(sub, false))
                    }
                  </div>
                )}

                {/* Sub-tab: Références */}
                {subTab === 'refs' && (
                  <div className="space-y-3">
                    {entityNewSubs.length === 0
                      ? renderEmptyVoterState('Aucune nouvelle référence en attente de vote')
                      : entityNewSubs.map(sub => renderVoteCard(sub, false))
                    }
                  </div>
                )}

                {/* Sub-tab: Corrections */}
                {subTab === 'corrections' && (
                  <div className="space-y-3">
                    {correctionItems.length === 0
                      ? renderEmptyVoterState('Aucune correction en attente de vote')
                      : correctionItems.map(item => {
                          const isReport = !item.submission_id;
                          return renderVoteCard(item, isReport);
                        })
                    }
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* TAB: SOUMETTRE                                                     */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {mainTab === 'soumettre' && (
          <div className="space-y-10">

            {/* Wizard form */}
            <div className="border border-primary/30 p-6">
              <h2 className="text-sm uppercase tracking-wider mb-6" style={{ fontFamily: 'Barlow Condensed' }}>
                Soumettre un maillot
              </h2>

              {/* Step indicator */}
              <div className="flex items-center gap-4 mb-6">
                <div className={`flex items-center gap-2 ${addStep === 1 ? 'text-primary' : 'text-muted-foreground'}`}>
                  <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 1 ? 'bg-primary text-primary-foreground' : addStep > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                    {addStep > 1 ? <Check className="w-3 h-3" /> : '1'}
                  </div>
                  <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>MASTER KIT</span>
                </div>
                <div className="w-8 h-px bg-border" />
                <div className={`flex items-center gap-2 ${addStep === 2 ? 'text-primary' : 'text-muted-foreground'}`}>
                  <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 2 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'}`}>2</div>
                  <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>VERSION</span>
                </div>
              </div>

              {/* Step 1 — Master Kit */}
              {addStep === 1 && (
                <div>
                  <UseExistingKitPanel onSelect={handleSelectExistingKit} />
                  <div className="text-center text-xs text-muted-foreground tracking-wider my-4" style={{ fontFamily: 'Barlow Condensed' }}>
                    OU CRÉER UN NOUVEAU KIT
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Team *</Label>
                      <EntityAutocomplete
                        entityType="team" value={club}
                        onChange={(val) => { setClub(val); setTeamId(''); setTeamIsNational(false); }}
                        onSelect={(item) => { setClub(item.label); setTeamId(item.id); setTeamIsNational(!!item.is_national); }}
                        placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" testId="add-club"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
                      <Input value={season} onChange={(e) => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>League</Label>
                      <EntityAutocomplete
                        entityType="league" value={league}
                        onChange={(val) => { setLeague(val); setLeagueId(''); }}
                        onSelect={(item) => { setLeague(item.label); setLeagueId(item.id); }}
                        placeholder="e.g., Ligue 1" className="bg-card border-border rounded-none" testId="add-league"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Type *</Label>
                      <Select value={kitType} onValueChange={setKitType}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select type" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Brand *</Label>
                      <EntityAutocomplete
                        entityType="brand" value={brand}
                        onChange={(val) => { setBrand(val); setBrandId(''); }}
                        onSelect={(item) => { setBrand(item.label); setBrandId(item.id); }}
                        placeholder="e.g., Nike" className="bg-card border-border rounded-none" testId="add-brand"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Design</Label>
                      <Input value={design} onChange={(e) => setDesign(e.target.value)} placeholder="e.g., Single stripe" className="bg-card border-border rounded-none" />
                    </div>
                    {!teamIsNational && (
                      <div className="space-y-2">
                        <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Sponsor</Label>
                        <EntityAutocomplete
                          entityType="sponsor" value={sponsor}
                          onChange={(val) => { setSponsor(val); setSponsorId(''); }}
                          onSelect={(item) => { setSponsor(item.label); setSponsorId(item.id); }}
                          placeholder="e.g., Qatar Airways" className="bg-card border-border rounded-none" testId="add-sponsor"
                        />
                      </div>
                    )}
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Gender</Label>
                      <Select value={gender} onValueChange={setGender}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select gender" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2 sm:col-span-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo *</Label>
                      <ImageUpload value={frontPhoto} onChange={setFrontPhoto} testId="add-front-photo" />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-6">
                    <Button onClick={handleSubmitKit} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
                      {submitting ? 'Envoi...' : 'Soumettre le Master Kit'} <ArrowRight className="w-4 h-4 ml-1" />
                    </Button>
                    <Button variant="outline" onClick={closeAddForm} className="rounded-none">Réinitialiser</Button>
                  </div>
                </div>
              )}

              {/* Step 2 — Version */}
              {addStep === 2 && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <button
                      onClick={() => { setAddStep(1); setSelectedKit(''); setSelectedKitLabel(''); }}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                      AJOUT D'UNE VERSION À{' '}
                      <span className="text-foreground">{selectedKitLabel || 'NOUVEAU KIT (EN ATTENTE)'}</span>
                    </span>
                  </div>
                  {!selectedKit && (
                    <div className="mb-4">
                      <Label className="text-xs uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed' }}>Select Parent Kit *</Label>
                      <Select value={selectedKit} onValueChange={setSelectedKit}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select a Master Kit" /></SelectTrigger>
                        <SelectContent className="bg-card border-border max-h-60">
                          {existingKits.map(k => (
                            <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Competition *</Label>
                      <Select value={competition} onValueChange={setCompetition}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select competition" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Model *</Label>
                      <Select value={model} onValueChange={setModel}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select model" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                      <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EAN Code</Label>
                      <Input value={eanCode} onChange={e => setEanCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                      <ImageUpload value={verFrontPhoto} onChange={setVerFrontPhoto} folder="version" side="front" testId="add-ver-front-photo" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Back Photo</Label>
                      <ImageUpload value={verBackPhoto} onChange={setVerBackPhoto} folder="version" side="back" testId="add-ver-back-photo" />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-6">
                    <Button onClick={handleSubmitVersion} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
                      {submitting ? 'Envoi...' : 'Soumettre la Version pour révision'} <Check className="w-4 h-4 ml-1" />
                    </Button>
                    <Button variant="outline" onClick={closeAddForm} className="rounded-none">Réinitialiser</Button>
                  </div>
                </div>
              )}
            </div>

            {/* Mes contributions */}
            {user && (
              <div>
                <h2 className="text-sm uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
                  Mes contributions
                </h2>
                {loadingMine ? (
                  <div className="space-y-2">
                    {[1, 2, 3].map(i => <div key={i} className="h-14 bg-card animate-pulse border border-border" />)}
                  </div>
                ) : myContributions.length === 0 ? (
                  <div className="text-center py-10 border border-dashed border-border">
                    <Package className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                      Vous n'avez pas encore soumis de contribution.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {myContributions.map(sub => (
                      <div
                        key={sub.submission_id}
                        className="flex items-center justify-between gap-3 border border-border bg-card px-4 py-3"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {getSubmissionTitle(sub, existingKits)}
                          </p>
                          <p className="text-[11px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {timeAgo(sub.created_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <Badge variant="outline" className={`rounded-none text-[10px] border ${statusBadgeClass(sub.status)}`}>
                            {sub.status}
                          </Badge>
                          {sub.status === 'pending' && (
                            <span className="font-mono text-[10px] text-muted-foreground">
                              ↑{sub.votes_up || 0} ↓{sub.votes_down || 0}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ══════════════════════════════════════════════════════════════════ */}
        {/* TAB: HISTORIQUE                                                    */}
        {/* ══════════════════════════════════════════════════════════════════ */}
        {mainTab === 'historique' && (
          <div className="space-y-12">

            {/* Derniers ajouts */}
            <section>
              <div className="flex items-center gap-3 mb-5">
                <Activity className="w-5 h-5 text-primary" />
                <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Derniers ajouts à la base</h2>
              </div>

              {loadingFeed ? (
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
                  {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="border border-border bg-card overflow-hidden">
                      <div className="aspect-[3/4] bg-secondary animate-pulse" />
                      <div className="p-2 space-y-1">
                        <div className="h-2.5 bg-secondary animate-pulse rounded w-3/4" />
                        <div className="h-2 bg-secondary animate-pulse rounded w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : recentApproved.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border">
                  <Package className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun ajout récent</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
                  {recentApproved.slice(0, 18).map(sub => (
                    <FeedCard key={sub.submission_id} sub={sub} />
                  ))}
                </div>
              )}
            </section>

            {/* Top contributeurs */}
            <section>
              <div className="flex items-center gap-3 mb-5">
                <Trophy className="w-5 h-5 text-yellow-500" />
                <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Meilleurs contributeurs</h2>
              </div>

              {loadingFeed ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="border border-border bg-card p-4 flex flex-col items-center gap-3">
                      <div className="w-16 h-16 rounded-full bg-secondary animate-pulse" />
                      <div className="space-y-2 w-full">
                        <div className="h-3 bg-secondary animate-pulse rounded w-2/3 mx-auto" />
                        <div className="h-2 bg-secondary animate-pulse rounded w-1/3 mx-auto" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : topContributors.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border">
                  <Users className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun contributeur pour le moment</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {topContributors.map((contributor, index) => (
                    <ContributorCard
                      key={contributor.username || contributor.name || index}
                      contributor={contributor}
                      rank={index + 1}
                    />
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

      </div>
    </div>
  );
}
