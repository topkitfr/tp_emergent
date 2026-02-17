import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getSubmissions, getReports, voteOnSubmission, voteOnReport, createSubmission, getMasterKits } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { ThumbsUp, ThumbsDown, Shirt, FileCheck, AlertTriangle, Plus, Check, Clock, X } from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special'];
const MODELS = ['Replica', 'Authentic', 'Player Issue'];
const GENDERS = ['Men', 'Women', 'Kids'];

export default function Contributions() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('pending');
  const [submissions, setSubmissions] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewForm, setShowNewForm] = useState(false);
  const [subType, setSubType] = useState('master_kit');
  const [existingKits, setExistingKits] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  // Form fields
  const [club, setClub] = useState('');
  const [season, setSeason] = useState('');
  const [kitType, setKitType] = useState('');
  const [brand, setBrand] = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());
  const [selectedKit, setSelectedKit] = useState('');
  const [competition, setCompetition] = useState('');
  const [model, setModel] = useState('');
  const [gender, setGender] = useState('');
  const [skuCode, setSkuCode] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const status = activeTab === 'approved' ? 'approved' : 'pending';
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status }),
        getReports({ status })
      ]);
      setSubmissions(subsRes.data);
      setReports(repsRes.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    getMasterKits({}).then(r => setExistingKits(r.data)).catch(() => {});
  }, [activeTab]);

  const handleVoteSub = async (subId, vote) => {
    try {
      await voteOnSubmission(subId, vote);
      toast.success(`Vote recorded: ${vote}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handleVoteReport = async (repId, vote) => {
    try {
      await voteOnReport(repId, vote);
      toast.success(`Vote recorded: ${vote}`);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      let data = {};
      if (subType === 'master_kit') {
        if (!club || !season || !kitType || !brand || !frontPhoto) {
          toast.error('Fill all required fields'); setSubmitting(false); return;
        }
        data = { club, season, kit_type: kitType, brand, front_photo: frontPhoto, year: parseInt(year) };
      } else {
        if (!selectedKit || !competition || !model || !gender) {
          toast.error('Fill all required fields'); setSubmitting(false); return;
        }
        data = { kit_id: selectedKit, competition, model, gender, sku_code: skuCode, front_photo: frontPhoto };
      }
      await createSubmission({ submission_type: subType, data });
      toast.success('Submission created! Community will review.');
      setShowNewForm(false);
      resetForm();
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setClub(''); setSeason(''); setKitType(''); setBrand('');
    setFrontPhoto(''); setYear(new Date().getFullYear());
    setSelectedKit(''); setCompetition(''); setModel(''); setGender(''); setSkuCode('');
  };

  const hasVoted = (item) => item.voters?.includes(user?.user_id);

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="contributions-title">
                CONTRIBUTIONS
              </h1>
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                Submit new jerseys and vote on community contributions. 5 upvotes required for approval.
              </p>
            </div>
            <Button onClick={() => setShowNewForm(!showNewForm)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0" data-testid="new-submission-btn">
              <Plus className="w-4 h-4 mr-1" /> New Submission
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8">
        {/* New Submission Form */}
        {showNewForm && (
          <div className="border border-primary/30 p-6 mb-8" data-testid="submission-form">
            <h3 className="text-lg tracking-tight mb-4">NEW SUBMISSION</h3>
            <div className="mb-4">
              <Label className="text-xs uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed' }}>Type</Label>
              <Select value={subType} onValueChange={setSubType}>
                <SelectTrigger className="bg-card border-border rounded-none w-48" data-testid="submission-type-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="master_kit">Master Kit</SelectItem>
                  <SelectItem value="version">Version</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {subType === 'master_kit' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Club *</Label>
                  <Input value={club} onChange={e => setClub(e.target.value)} placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" data-testid="sub-club" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
                  <Input value={season} onChange={e => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" data-testid="sub-season" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Type *</Label>
                  <Select value={kitType} onValueChange={setKitType}>
                    <SelectTrigger className="bg-card border-border rounded-none" data-testid="sub-kit-type"><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Brand *</Label>
                  <Input value={brand} onChange={e => setBrand(e.target.value)} placeholder="e.g., Nike" className="bg-card border-border rounded-none" data-testid="sub-brand" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Year</Label>
                  <Input type="number" value={year} onChange={e => setYear(e.target.value)} className="bg-card border-border rounded-none" data-testid="sub-year" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Photo *</Label>
                  <ImageUpload value={frontPhoto} onChange={setFrontPhoto} testId="sub-photo-upload" />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2 sm:col-span-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Master Kit *</Label>
                  <Select value={selectedKit} onValueChange={setSelectedKit}>
                    <SelectTrigger className="bg-card border-border rounded-none" data-testid="sub-kit-select"><SelectValue placeholder="Select kit" /></SelectTrigger>
                    <SelectContent className="bg-card border-border max-h-60">
                      {existingKits.map(k => <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Competition *</Label>
                  <Input value={competition} onChange={e => setCompetition(e.target.value)} placeholder="e.g., Champions League" className="bg-card border-border rounded-none" data-testid="sub-competition" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Model *</Label>
                  <Select value={model} onValueChange={setModel}>
                    <SelectTrigger className="bg-card border-border rounded-none" data-testid="sub-model"><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Gender *</Label>
                  <Select value={gender} onValueChange={setGender}>
                    <SelectTrigger className="bg-card border-border rounded-none" data-testid="sub-gender"><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      {GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                  <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} className="bg-card border-border rounded-none font-mono" data-testid="sub-sku" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Photo</Label>
                  <ImageUpload value={frontPhoto} onChange={setFrontPhoto} testId="sub-ver-photo-upload" />
                </div>
              </div>
            )}

            <div className="flex gap-2 mt-6">
              <Button onClick={handleSubmit} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="submit-contribution-btn">
                {submitting ? 'Submitting...' : 'Submit for Review'}
              </Button>
              <Button variant="outline" onClick={() => { setShowNewForm(false); resetForm(); }} className="rounded-none" data-testid="cancel-submission-btn">
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-card border border-border rounded-none mb-6">
            <TabsTrigger value="pending" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground" data-testid="tab-pending">
              <Clock className="w-3 h-3 mr-1" /> Pending
            </TabsTrigger>
            <TabsTrigger value="approved" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground" data-testid="tab-approved">
              <Check className="w-3 h-3 mr-1" /> Approved
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {/* Submissions */}
            <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
              <Shirt className="w-4 h-4 inline mr-1" /> JERSEY SUBMISSIONS
            </h3>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => <div key={i} className="h-20 bg-card animate-pulse border border-border" />)}
              </div>
            ) : submissions.length === 0 ? (
              <div className="text-center py-10 border border-dashed border-border mb-8">
                <FileCheck className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                  No {activeTab} submissions
                </p>
              </div>
            ) : (
              <div className="space-y-3 mb-8" data-testid="submissions-list">
                {submissions.map(sub => (
                  <div key={sub.submission_id} className="border border-border p-4 bg-card" data-testid={`submission-${sub.submission_id}`}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <Badge variant="outline" className="rounded-none text-[10px]">{sub.submission_type === 'master_kit' ? 'Master Kit' : 'Version'}</Badge>
                          <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>
                            {sub.status}
                          </Badge>
                        </div>
                        <h4 className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {sub.submission_type === 'master_kit'
                            ? `${sub.data?.club || '?'} - ${sub.data?.season || '?'} (${sub.data?.kit_type || '?'})`
                            : `${sub.data?.competition || '?'} - ${sub.data?.model || '?'}`}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          by {sub.submitter_name || 'Unknown'} -- {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-center">
                          <div className="flex items-center gap-1">
                            <span className="font-mono text-sm text-primary">{sub.votes_up}</span>
                            <span className="text-muted-foreground">/</span>
                            <span className="font-mono text-sm text-destructive">{sub.votes_down}</span>
                          </div>
                          <span className="text-[10px] text-muted-foreground">votes</span>
                        </div>
                        {sub.status === 'pending' && !hasVoted(sub) && (
                          <div className="flex gap-1">
                            <button onClick={() => handleVoteSub(sub.submission_id, 'up')} className="p-2 border border-border hover:border-primary hover:text-primary" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-up-${sub.submission_id}`}>
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleVoteSub(sub.submission_id, 'down')} className="p-2 border border-border hover:border-destructive hover:text-destructive" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-down-${sub.submission_id}`}>
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                        {hasVoted(sub) && (
                          <Badge variant="secondary" className="rounded-none text-[10px]">Voted</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Reports */}
            <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
              <AlertTriangle className="w-4 h-4 inline mr-1" /> CORRECTION REPORTS
            </h3>
            {reports.length === 0 ? (
              <div className="text-center py-10 border border-dashed border-border">
                <AlertTriangle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                  No {activeTab} reports
                </p>
              </div>
            ) : (
              <div className="space-y-3" data-testid="reports-list">
                {reports.map(rep => (
                  <div key={rep.report_id} className="border border-border p-4 bg-card" data-testid={`report-${rep.report_id}`}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <Badge variant="outline" className="rounded-none text-[10px]">{rep.target_type === 'master_kit' ? 'Kit Correction' : 'Version Correction'}</Badge>
                          <Badge className={`rounded-none text-[10px] ${rep.status === 'approved' ? 'bg-primary/20 text-primary' : 'bg-accent/20 text-accent'}`}>
                            {rep.status}
                          </Badge>
                        </div>
                        <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {rep.notes || 'Correction submitted'}
                        </p>
                        <div className="mt-2 grid grid-cols-2 gap-2">
                          <div className="p-2 bg-destructive/5 border border-destructive/20">
                            <p className="text-[10px] text-destructive uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Original</p>
                            <pre className="text-[10px] text-muted-foreground font-mono overflow-hidden">{JSON.stringify(rep.original_data, null, 1).slice(0, 150)}...</pre>
                          </div>
                          <div className="p-2 bg-primary/5 border border-primary/20">
                            <p className="text-[10px] text-primary uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Proposed</p>
                            <pre className="text-[10px] text-muted-foreground font-mono overflow-hidden">{JSON.stringify(rep.corrections, null, 1).slice(0, 150)}...</pre>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-2" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          by {rep.reporter_name || 'Unknown'}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-center">
                          <div className="flex items-center gap-1">
                            <span className="font-mono text-sm text-primary">{rep.votes_up}</span>
                            <span className="text-muted-foreground">/</span>
                            <span className="font-mono text-sm text-destructive">{rep.votes_down}</span>
                          </div>
                          <span className="text-[10px] text-muted-foreground">votes</span>
                        </div>
                        {rep.status === 'pending' && !hasVoted(rep) && (
                          <div className="flex gap-1">
                            <button onClick={() => handleVoteReport(rep.report_id, 'up')} className="p-2 border border-border hover:border-primary hover:text-primary" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-up-rep-${rep.report_id}`}>
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button onClick={() => handleVoteReport(rep.report_id, 'down')} className="p-2 border border-border hover:border-destructive hover:text-destructive" style={{ transition: 'border-color 0.2s, color 0.2s' }} data-testid={`vote-down-rep-${rep.report_id}`}>
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                        {hasVoted(rep) && (
                          <Badge variant="secondary" className="rounded-none text-[10px]">Voted</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
