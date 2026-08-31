-- =============================================================================
-- AI Pathfinder Database Schema & Migration Script
-- Compatible with Supabase / PostgreSQL 15+
-- =============================================================================

-- Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. Users Table (Syncs with Supabase Auth or standalone user management)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for username lookups (public portfolios)
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users (username);

-- -----------------------------------------------------------------------------
-- 2. Learner Profiles Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.learner_profiles (
    user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    target_role TEXT NOT NULL,
    weekly_hours INTEGER NOT NULL DEFAULT 10,
    learning_pace TEXT NOT NULL DEFAULT 'medium' CHECK (learning_pace IN ('slow', 'medium', 'fast')),
    skills JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 3. Roadmaps Table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    target_role TEXT NOT NULL,
    total_estimated_weeks INTEGER NOT NULL DEFAULT 0,
    total_hours INTEGER NOT NULL DEFAULT 0,
    learner_summary TEXT,
    skill_gap_summary JSONB DEFAULT '[]'::jsonb,
    graph_payload JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes for active roadmap lookup & public portfolio lookup
CREATE INDEX IF NOT EXISTS idx_roadmaps_user_active ON public.roadmaps (user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_roadmaps_user_public ON public.roadmaps (user_id, is_public);

-- -----------------------------------------------------------------------------
-- 4. Milestone Progress Tracking
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.milestone_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES public.roadmaps(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('locked', 'available', 'in_progress', 'completed')),
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(roadmap_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_milestone_progress_lookup ON public.milestone_progress (roadmap_id, node_id);

-- -----------------------------------------------------------------------------
-- 5. Peer Study Cohorts
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.cohorts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic TEXT NOT NULL,
    target_role TEXT NOT NULL,
    max_members INTEGER NOT NULL DEFAULT 8,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cohorts_target_role ON public.cohorts (target_role);

-- -----------------------------------------------------------------------------
-- 6. Cohort Memberships
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.cohort_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cohort_id UUID NOT NULL REFERENCES public.cohorts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(cohort_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_cohort_members_user ON public.cohort_members (user_id);
CREATE INDEX IF NOT EXISTS idx_cohort_members_cohort ON public.cohort_members (cohort_id);

-- -----------------------------------------------------------------------------
-- 7. Row Level Security (RLS) Policies
-- -----------------------------------------------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learner_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.milestone_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cohort_members ENABLE ROW LEVEL SECURITY;

-- Users RLS
CREATE POLICY "Users can view all public usernames" ON public.users FOR SELECT USING (true);
CREATE POLICY "Users can update their own data" ON public.users FOR ALL USING (auth.uid() = id);

-- Learner Profiles RLS
CREATE POLICY "Users can manage their own profile" ON public.learner_profiles FOR ALL USING (auth.uid() = user_id);

-- Roadmaps RLS
CREATE POLICY "Public roadmaps are viewable by everyone" ON public.roadmaps FOR SELECT USING (is_public = true OR auth.uid() = user_id);
CREATE POLICY "Users can manage their own roadmaps" ON public.roadmaps FOR ALL USING (auth.uid() = user_id);

-- Milestone Progress RLS
CREATE POLICY "Users can manage milestone progress on their roadmaps" ON public.milestone_progress FOR ALL 
USING (EXISTS (SELECT 1 FROM public.roadmaps WHERE roadmaps.id = milestone_progress.roadmap_id AND roadmaps.user_id = auth.uid()));

-- Cohorts RLS
CREATE POLICY "Cohorts viewable by authenticated users" ON public.cohorts FOR SELECT TO authenticated USING (true);

-- Cohort Members RLS
CREATE POLICY "Cohort members viewable by authenticated users" ON public.cohort_members FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can join/leave cohorts" ON public.cohort_members FOR ALL TO authenticated USING (auth.uid() = user_id);

-- -----------------------------------------------------------------------------
-- 8. Auth Trigger to Auto-create Public User Record on Signup
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.users (id, email, username)
  VALUES (
    new.id,
    new.email,
    COALESCE(new.raw_user_meta_data->>'username', split_part(new.email, '@', 1))
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    username = COALESCE(new.raw_user_meta_data->>'username', public.users.username);
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger execution on auth.users insert
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
