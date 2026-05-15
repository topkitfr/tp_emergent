import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Link } from 'react-router-dom';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Shirt, FileCheck, AlertTriangle, Plus, Check, Clock, X,
  ArrowLeft, CheckCircle2, Trophy, Activity, Users, Package,
} from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import {
  KIT_TYPES, MODELS, GENDERS, COMPETITIONS, SEASONS,
  emptyEntityBuckets, buildEntityBucketsFromSubmissions, getSubmissionTitle,
  FeedCard, ContributorCard, SubmissionDetail, ReportDetail,
  UseExistingKitPanel, VoteRow, TYPE_LABELS, TYPE_COLORS, UserLink, getDisplayName,
} from '@/components/ContributionComponents';

// ===== COMPOSANT PRINCIPAL =====
export default function Contributions() {
  const { user } = useAuth();

  const [activeTab, setActiveTab]               = useState('pending');
  const [submissions, setSubmissions]           = useState([]);
  const [reports, setReports]                   = useState([]);
  const [loading, setLoading]                   = useState(true);
  const [existingKits, setExistingKits]         = useState([]);
  const [expandedSubmission, setExpandedSubmission] = useState(null);
  const [expandedReport, setExpandedReport]     = useState(null);
  const [pendingEntities, setPendingEntities]   = useState(emptyEntityBuckets());
  const [approvedEntities, setApprovedEntities] = useState(emptyEntityBuckets());
  const [loadingPending, setLoadingPending]     = useState(false);

  const [recentApproved, setRecentApproved]     = useState([]);
  const [loadingFeed, setLoadingFeed]           = useState(true);
  const [topContributors, setTopContributors]   = useState([]);

  const [showAddForm, setShowAddForm]           = useState(false);
  const [addStep, setAddStep]                   = useState(1);
  const [subType, setSubType]                   = useState('master_kit');
  const [submitting, setSubmitting]             = useState(false);

  const [club, setClub]           = useState('');
  const [teamId, setTeamId]       = useState('');
  // is_national de la team sélectionnée — pilote l'affichage du champ
  // Sponsor (sponsoring maillot interdit FIFA pour les équipes nationales).
  // Reset à null si on retape à la main (pas d'item DB sélectionné).
  const [teamIsNational, setTeamIsNational] = useState(false);
  const [season, setSeason]       = useState('');
  const [kitType, setKitType]     = useState('');
  const [brand, setBrand]         = useState('');
  const [brandId, setBrandId]     = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [design, setDesign]       = useState('');
  const [sponsor, setSponsor]     = useState('');
  const [sponsorId, setSponsorId] = useState('');
  const [leagueId, setLeagueId]   = useState('');
  const [league, setLeague]       = useState('');
  const [gender, setGender]       = useState('');

  const [selectedKit, setSelectedKit]           = useState('');
  const [selectedKitLabel, setSelectedKitLabel] = useState('');
  const [competition, setCompetition]           = useState('');
  const [model, setModel]                       = useState('');
  const [skuCode, setSkuCode]                   = useState('');
  const [eanCode, setEanCode]                   = useState('');
  const [verFrontPhoto, setVerFrontPhoto]       = useState('');
  const [verBackPhoto, setVerBackPhoto]         = useState('');

  // ===== FETCH FEED + CONTRIBUTORS =====
  useEffect(() => {
    async function fetchFeedData() {
      setLoadingFeed(true);
      try {
        const res = await getSubmissions({ status: 'approved', limit: 30 });
        const approved = res.data || [];
        setRecentApproved(approved);

        // Agréger les top contributeurs
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

        // Fetch photo_url pour chaque contributeur qui a un username
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
      } catch (e) {
        console.error('Failed to fetch feed:', e);
      } finally {
        setLoadingFeed(false);
      }
    }
    fetchFeedData();
  }, []);

  // ===== FETCH QUEUE =====
  const fetchData = useCallback(async () => {
    setLoading(true);
    setLoadingPending(true);
    try {
      const status = activeTab === 'approved' ? 'approved' : activeTab === 'rejected' ? 'rejected' : 'pending';
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status }),
        getReports({ status }),
      ]);
      const nextSubs = subsRes.data || [];
      setSubmissions(nextSubs);
      setReports(repsRes.data || []);
      const entityBuckets = buildEntityBucketsFromSubmissions(nextSubs);
      if (status === 'approved') {
        setApprovedEntities(entityBuckets);
        setPendingEntities(emptyEntityBuckets());
      } else {
        setPendingEntities(entityBuckets);
        setApprovedEntities(emptyEntityBuckets());
      }
    } catch (e) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
      setLoadingPending(false);
    }
  }, [activeTab]);

  useEffect(() => { fetchData(); }, [activeTab, fetchData]);

  useEffect(() => {
    getMasterKits({ limit: 500 }).then(res => setExistingKits(res.data?.results ?? [])).catch(console.error);
  }, []);

  // ===== SUBMIT =====
  const handleSubmitKit = async () => {
    if (!club.trim() || !season.trim() || !kitType || !brand.trim() || !frontPhoto) {
      toast.error('Please fill all required fields (Club, Season, Type, Brand, Photo)'); return;
    }
    setSubmitting(true);
    try {
      // Équipes nationales : pas de sponsor maillot (règle FIFA), on n'envoie
      // ni le nom ni l'id pour éviter de polluer la submission avec des restes
      // de saisie d'une team précédente.
      const effSponsor   = teamIsNational ? '' : sponsor;
      const effSponsorId = teamIsNational ? '' : sponsorId;
      const data = { club, team_id: teamId, season, kit_type: kitType, brand, brand_id: brandId, league, league_id: leagueId, sponsor: effSponsor, sponsor_id: effSponsorId, design, gender, front_photo: frontPhoto };
      const submissionRes = await createSubmission({ submission_type: 'master_kit', data });
      const masterKitSubmissionId = submissionRes?.data?.submission_id;
      if (masterKitSubmissionId) {
        const pendingJobs = [];
        if (!teamId    && club.trim())    pendingJobs.push(createTeamPending(   { name: club.trim()    }, masterKitSubmissionId));
        if (!brandId   && brand.trim())   pendingJobs.push(createBrandPending(  { name: brand.trim()   }, masterKitSubmissionId));
        if (!leagueId  && league.trim())  pendingJobs.push(createLeaguePending( { name: league.trim()  }, masterKitSubmissionId));
        if (!effSponsorId && effSponsor.trim()) pendingJobs.push(createSponsorPending({ name: effSponsor.trim() }, masterKitSubmissionId));
        await Promise.allSettled(pendingJobs);
      }
      toast.success('Master kit submitted for community review!');
      closeAddForm();
      await fetchData();
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
      await createSubmission({ submission_type: 'version', data: { kit_id: selectedKit, competition, model, sku_code: skuCode, ean_code: eanCode, front_photo: verFrontPhoto, back_photo: verBackPhoto } });
      toast.success('Version submitted for community review!');
      closeAddForm();
      await fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const closeAddForm = () => {
    setShowAddForm(false); setAddStep(1); setSubType('master_kit');
    setClub(''); setTeamId(''); setTeamIsNational(false); setSponsorId(''); setSeason(''); setKitType(''); setBrand(''); setBrandId('');
    setFrontPhoto(''); setDesign(''); setSponsor(''); setLeague(''); setLeagueId(''); setGender('');
    setSelectedKit(''); setSelectedKitLabel(''); setCompetition(''); setModel('');
    setSkuCode(''); setEanCode(''); setVerFrontPhoto(''); setVerBackPhoto('');
  };

  const handleSelectExistingKit = (kit) => {
    setSelectedKit(kit.kit_id);
    setSelectedKitLabel(`${kit.club} — ${kit.season} (${kit.kit_type})`);
    setAddStep(2); setSubType('version');
  };

  const hasVoted = (item) => item.voters?.includes(user?.user_id);
  const isModerator = user?.role === 'moderator' || user?.role === 'admin';

  const handleVoteSubmission = async (submissionId, isUpvote) => {
    try {
      await voteOnSubmission(submissionId, isUpvote ? 'up' : 'down');
      await fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to register vote');
    }
  };

  const handleVoteReport = async (reportId, vote) => {
    try {
      await voteOnReport(reportId, vote);
      await fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to register vote');
    }
  };

  const entityEditSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    ['edit', 'removal'].includes(s.data?.mode)
  );
  const entityCreateSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    s.data?.mode === 'create'
  );
  const standaloneEntitySubs = entityCreateSubs.filter(s => !s.data?.parent_submission_id);
  const jerseyAndCreateSubs = submissions.filter(s =>
    !entityEditSubs.includes(s) &&
    !entityCreateSubs.includes(s) &&
    (s.submission_type === 'master_kit' || s.submission_type === 'version')
  );

  const totalApproved = recentApproved.length;
  const pendingCount = submissions.filter(s => s.status === 'pending').length + reports.filter(r => r.status === 'pending').length;

  return (
    <div className="animate-fade-in-up">

      {/* ===== HEADER ===== */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2">CONTRIBUTIONS</h1>
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                Suivez les ajouts de la communauté, votez sur les soumissions en attente, et découvrez les meilleurs contributeurs.
                {isModerator ? ' En tant que modérateur, votre vote valide instantanément.' : ' 5 votes requis pour validation.'}
              </p>
              {isModerator && <Badge className="mt-2 rounded-none bg-primary/20 text-primary border-primary/30">Moderator</Badge>}
            </div>
            <Button onClick={() => setShowAddForm(!showAddForm)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0">
              <Plus className="w-4 h-4 mr-1" /> Add Jersey
            </Button>
          </div>

          <div className="flex items-center gap-6 mt-6 pt-6 border-t border-border">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{totalApproved}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>ajouts récents</span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{pendingCount}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>en attente de vote</span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{topContributors.length}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>contributeurs actifs</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8 space-y-12">

        {/* ===== FORMULAIRE ADD ===== */}
        {showAddForm && (
          <div className="border border-primary/30 p-6">
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

            {addStep === 1 && (
              <div>
                <UseExistingKitPanel onSelect={handleSelectExistingKit} />
                <div className="text-center text-xs text-muted-foreground tracking-wider my-4" style={{ fontFamily: 'Barlow Condensed' }}>OR CREATE NEW</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Team *</Label>
                    <EntityAutocomplete entityType="team" value={club}
                      onChange={(val) => { setClub(val); setTeamId(''); setTeamIsNational(false); }}
                      onSelect={(item) => { setClub(item.label); setTeamId(item.id); setTeamIsNational(!!item.is_national); }}
                      placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" testId="add-club" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
                    <Input value={season} onChange={(e) => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>League</Label>
                    <EntityAutocomplete entityType="league" value={league}
                      onChange={(val) => { setLeague(val); setLeagueId(''); }}
                      onSelect={(item) => { setLeague(item.label); setLeagueId(item.id); }}
                      placeholder="e.g., Ligue 1" className="bg-card border-border rounded-none" testId="add-league" />
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
                    <EntityAutocomplete entityType="brand" value={brand}
                      onChange={(val) => { setBrand(val); setBrandId(''); }}
                      onSelect={(item) => { setBrand(item.label); setBrandId(item.id); }}
                      placeholder="e.g., Nike" className="bg-card border-border rounded-none" testId="add-brand" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Design</Label>
                    <Input value={design} onChange={(e) => setDesign(e.target.value)} placeholder="e.g., Single stripe" className="bg-card border-border rounded-none" />
                  </div>
                  {!teamIsNational && (
                    <div className="space-y-2">
                      <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Sponsor</Label>
                      <EntityAutocomplete entityType="sponsor" value={sponsor}
                        onChange={(val) => { setSponsor(val); setSponsorId(''); }}
                        onSelect={(item) => { setSponsor(item.label); setSponsorId(item.id); }}
                        placeholder="e.g., Qatar Airways" className="bg-card border-border rounded-none" testId="add-sponsor" />
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
                    {submitting ? 'Submitting...' : 'Submit Master Kit'} <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none">Cancel</Button>
                </div>
              </div>
            )}

            {addStep === 2 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <button onClick={() => { setAddStep(1); setSelectedKit(''); setSelectedKitLabel(''); }} className="text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                    ADDING VERSION TO{' '}
                    <span className="text-foreground">{selectedKitLabel || 'NEW KIT (PENDING)'}</span>
                  </span>
                </div>
                {!selectedKit && (
                  <div className="mb-4">
                    <Label className="text-xs uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed' }}>Select Parent Kit *</Label>
                    <Select value={selectedKit} onValueChange={setSelectedKit}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select a Master Kit" /></SelectTrigger>
                      <SelectContent className="bg-card border-border max-h-60">
                        {existingKits.map(k => <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>)}
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
                    {submitting ? 'Submitting...' : 'Submit Version for Review'} <Check className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none">Cancel</Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===== SECTION 1 : DERNIERS AJOUTS (image cards) ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <Activity className="w-5 h-5 text-primary" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Derniers ajouts à la base</h2>
          </div>

          {loadingFeed ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {[1,2,3,4,5,6].map(i => (
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

        {/* ===== SECTION 2 : TOP CONTRIBUTEURS ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <Trophy className="w-5 h-5 text-yellow-500" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Meilleurs contributeurs</h2>
          </div>

          {loadingFeed ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[1,2,3,4,5,6].map(i => (
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
                <ContributorCard key={contributor.username || contributor.name || index} contributor={contributor} rank={index + 1} />
              ))}
            </div>
          )}
        </section>

        {/* ===== SECTION 3 : COMMUNITY QUEUE ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <ThumbsUp className="w-5 h-5 text-primary" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Community Queue — Votes</h2>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="bg-card border border-border rounded-none mb-6">
              <TabsTrigger value="pending" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Clock className="w-3 h-3 mr-1" /> Pending
              </TabsTrigger>
              <TabsTrigger value="approved" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Check className="w-3 h-3 mr-1" /> Approved
              </TabsTrigger>
              <TabsTrigger value="rejected" className="rounded-none data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
                <X className="w-3 h-3 mr-1" /> Rejected
              </TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab}>
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                <Shirt className="w-4 h-4" /> Jersey Submissions
              </h3>
              {loading ? (
                <div className="space-y-3 mb-8">{[1,2,3].map(i => <div key={i} className="h-20 bg-card animate-pulse border border-border" />)}</div>
              ) : jerseyAndCreateSubs.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border mb-8">
                  <FileCheck className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No {activeTab} submissions</p>
                </div>
              ) : (
                <div className="space-y-3 mb-8">
                  {jerseyAndCreateSubs.map(sub => (
                    <VoteRow
                      key={sub.submission_id}
                      item={sub}
                      onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                      onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                      hasVoted={hasVoted(sub)}
                      expanded={expandedSubmission === sub.submission_id}
                      onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                      title={getSubmissionTitle(sub, existingKits)}
                      subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                        {sub.data?.mode === 'removal' && <Badge variant="outline" className="rounded-none text-[10px] border-destructive/50 text-destructive">Removal</Badge>}
                        <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                      </>}
                    >
                      <SubmissionDetail sub={sub} existingKits={existingKits} />
                    </VoteRow>
                  ))}
                </div>
              )}

              {standaloneEntitySubs.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <Package className="w-4 h-4" /> Database References
                  </h3>
                  <div className="space-y-3">
                    {standaloneEntitySubs.map(sub => (
                      <VoteRow
                        key={sub.submission_id}
                        item={sub}
                        onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                        onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                        hasVoted={hasVoted(sub)}
                        expanded={expandedSubmission === sub.submission_id}
                        onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                        title={sub.submission_type === 'player' ? (sub.data?.full_name || '?') : (sub.data?.name || '?')}
                        subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                        badges={<>
                          <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                          <Badge variant="outline" className="rounded-none text-[10px] border-primary/30 text-primary">New</Badge>
                          <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                        </>}
                      >
                        <SubmissionDetail sub={sub} existingKits={existingKits} />
                      </VoteRow>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'pending' && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <AlertTriangle className="w-4 h-4" /> Références en attente de validation
                  </h3>
                  {loadingPending ? (
                    <div className="h-16 bg-card animate-pulse border border-border" />
                  ) : Object.values(pendingEntities).every(arr => arr.length === 0) ? (
                    <div className="text-center py-8 border border-dashed border-border">
                      <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucune référence en attente</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {[{ key: 'team', label: 'Équipes' }, { key: 'league', label: 'Compétitions' }, { key: 'brand', label: 'Marques' }, { key: 'player', label: 'Joueurs' }, { key: 'sponsor', label: 'Sponsors' }].map(({ key, label }) => {
                        const list = pendingEntities[key] || [];
                        if (!list.length) return null;
                        return (
                          <div key={key} className="border border-border bg-card p-4">
                            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{label} ({list.length})</p>
                            <div className="space-y-2">
                              {list.map(item => (
                                <div key={item._id} className="flex items-center justify-between px-3 py-2 bg-secondary/30 border border-border/50">
                                  <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getDisplayName(item)}</span>
                                  <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent">for review</Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'approved' && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <CheckCircle2 className="w-4 h-4" /> Références validées
                  </h3>
                  {Object.values(approvedEntities).every(arr => arr.length === 0) ? (
                    <div className="text-center py-8 border border-dashed border-border">
                      <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No approved references yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {[{ key: 'team', label: 'Équipes' }, { key: 'league', label: 'Compétitions' }, { key: 'brand', label: 'Marques' }, { key: 'player', label: 'Joueurs' }, { key: 'sponsor', label: 'Sponsors' }].map(({ key, label }) => {
                        const list = approvedEntities[key] || [];
                        if (!list.length) return null;
                        return (
                          <div key={key} className="border border-border bg-card p-4">
                            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{label} ({list.length})</p>
                            <div className="space-y-2">
                              {list.map(item => (
                                <div key={item._id} className="flex items-center justify-between px-3 py-2 bg-secondary/30 border border-border/50">
                                  <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getDisplayName(item)}</span>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="rounded-none text-[10px] border-primary/40 text-primary">approved</Badge>
                                    <Link to={`/${key}/${item.slug || item._id}`} className="text-xs text-primary hover:underline">View</Link>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                <AlertTriangle className="w-4 h-4" /> Correction Reports
              </h3>
              {reports.length === 0 && entityEditSubs.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border">
                  <AlertTriangle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No {activeTab} reports</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {reports.map(rep => (
                    <VoteRow
                      key={rep.report_id}
                      item={rep}
                      onVoteUp={() => handleVoteReport(rep.report_id, 'up')}
                      onVoteDown={() => handleVoteReport(rep.report_id, 'down')}
                      hasVoted={hasVoted(rep)}
                      expanded={expandedReport === rep.report_id}
                      onToggle={() => setExpandedReport(expandedReport === rep.report_id ? null : rep.report_id)}
                      title={rep.notes || 'Correction submitted'}
                      subtitle={<>by <UserLink name={rep.reporter_name} username={rep.reporter_username} /> — {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">
                          {rep.report_type === 'removal' ? 'Removal Request' : rep.target_type === 'master_kit' ? 'Kit Correction' : 'Version Correction'}
                        </Badge>
                        <Badge className={`rounded-none text-[10px] ${rep.status === 'approved' ? 'bg-primary/20 text-primary' : rep.status === 'rejected' ? 'bg-destructive/20 text-destructive' : 'bg-accent/20 text-accent'}`}>{rep.status}</Badge>
                      </>}
                    >
                      <ReportDetail rep={rep} />
                    </VoteRow>
                  ))}
                  {entityEditSubs.map(sub => (
                    <VoteRow
                      key={sub.submission_id}
                      item={sub}
                      onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                      onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                      hasVoted={hasVoted(sub)}
                      expanded={expandedSubmission === sub.submission_id}
                      onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                      title={sub.submission_type === 'player' ? (sub.data?.full_name || '?') : (sub.data?.name || '?')}
                      subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                        <Badge variant="outline" className="rounded-none text-[10px] border-orange-500/40 text-orange-500">
                          {sub.data?.mode === 'removal' ? 'Removal' : 'Edit'}
                        </Badge>
                        <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                      </>}
                    >
                      <SubmissionDetail sub={sub} existingKits={existingKits} />
                    </VoteRow>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </section>
      </div>
    </div>
  );
}
