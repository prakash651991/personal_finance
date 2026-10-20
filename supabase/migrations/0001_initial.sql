-- Initial schema
create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  default_currency char(3) not null default 'INR',
  timezone text not null default 'Asia/Kolkata',
  budget_period_start_day int not null default 1,
  notification_prefs jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
create policy "profiles own" on public.profiles for all to authenticated using (auth.uid() = id) with check (auth.uid() = id);

create table if not exists public.accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  institution text,
  account_type text not null check (account_type in ('bank','cash','savings','other')),
  opening_balance numeric(14,2) not null default 0,
  opening_balance_date date,
  is_active boolean not null default true,
  archived_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.accounts enable row level security;
create policy "accounts own" on public.accounts for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index idx_accounts_user on public.accounts(user_id);

create table if not exists public.categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  parent_id uuid references public.categories(id) on delete set null,
  is_system boolean not null default false,
  created_at timestamptz not null default now()
);
alter table public.categories enable row level security;
create policy "categories own or system" on public.categories for all to authenticated
  using (user_id is null or auth.uid() = user_id)
  with check (user_id is null or auth.uid() = user_id);
create index idx_categories_user on public.categories(user_id);

create table if not exists public.income_sources (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  source_type text not null default 'other',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.income_sources enable row level security;
create policy "income_sources own" on public.income_sources for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  account_id uuid references public.accounts(id) on delete set null,
  transaction_type text not null check (transaction_type in ('income','expense','refund','transfer','credit_card_purchase','credit_card_payment','loan_disbursement','loan_repayment','savings_contribution','savings_withdrawal','adjustment')),
  amount numeric(14,2) not null check (amount > 0),
  currency char(3) not null default 'INR',
  transaction_date date not null,
  posting_date date,
  category_id uuid references public.categories(id) on delete set null,
  income_source_id uuid references public.income_sources(id) on delete set null,
  description text,
  notes text,
  transfer_group_id uuid,
  linked_transaction_id uuid references public.transactions(id) on delete set null,
  status text not null default 'posted' check (status in ('draft','posted','reversed','archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.transactions enable row level security;
create policy "transactions own" on public.transactions for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index idx_transactions_user_date on public.transactions(user_id, transaction_date desc);
create index idx_transactions_user_type_date on public.transactions(user_id, transaction_type, transaction_date desc);

create table if not exists public.credit_cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  nickname text not null,
  issuer text,
  last4 char(4),
  credit_limit numeric(14,2),
  statement_day int,
  due_day int,
  cycle_rule text not null default 'standard',
  is_active boolean not null default true,
  archived_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.credit_cards enable row level security;
create policy "credit_cards own" on public.credit_cards for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.credit_card_statements (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id uuid not null references public.credit_cards(id) on delete cascade,
  period_start date not null,
  period_end date not null,
  statement_date date,
  status text not null default 'estimated' check (status in ('estimated','issued','paid','partial','overdue')),
  statement_total numeric(14,2) not null default 0,
  minimum_due numeric(14,2),
  due_date date,
  paid_amount numeric(14,2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.credit_card_statements enable row level security;
create policy "cc_statements own" on public.credit_card_statements for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.credit_card_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id uuid not null references public.credit_cards(id) on delete cascade,
  transaction_id uuid references public.transactions(id) on delete set null,
  kind text not null check (kind in ('purchase','fee','interest','refund','payment')),
  purchase_date date not null,
  posting_date date,
  statement_id uuid references public.credit_card_statements(id) on delete set null,
  amount numeric(14,2) not null check (amount > 0),
  description text,
  issuer_ref text,
  created_at timestamptz not null default now()
);
alter table public.credit_card_transactions enable row level security;
create policy "cc_tx own" on public.credit_card_transactions for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create unique index if not exists uq_cc_tx_issuer on public.credit_card_transactions(user_id, card_id, issuer_ref) where issuer_ref is not null;

create table if not exists public.credit_card_payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id uuid not null references public.credit_cards(id) on delete cascade,
  transaction_id uuid references public.transactions(id) on delete set null,
  statement_id uuid references public.credit_card_statements(id) on delete set null,
  payment_date date not null,
  amount numeric(14,2) not null check (amount > 0),
  created_at timestamptz not null default now()
);
alter table public.credit_card_payments enable row level security;
create policy "cc_payments own" on public.credit_card_payments for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.loans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  lender_name text,
  loan_type text not null default 'personal',
  start_date date not null,
  end_date date not null,
  first_emi_date date,
  emi_due_day int,
  emi_amount numeric(14,2) not null check (emi_amount > 0),
  original_principal numeric(14,2),
  annual_interest_rate numeric(8,4),
  interest_type text,
  payment_account_id uuid references public.accounts(id) on delete set null,
  status text not null default 'active' check (status in ('active','closed','archived')),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (end_date >= start_date)
);
alter table public.loans enable row level security;
create policy "loans own" on public.loans for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.loan_installments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  loan_id uuid not null references public.loans(id) on delete cascade,
  installment_number int not null,
  due_date date not null,
  expected_amount numeric(14,2) not null,
  paid_amount numeric(14,2) not null default 0,
  paid_date date,
  status text not null default 'upcoming' check (status in ('upcoming','partial','paid','overdue','skipped')),
  principal_component numeric(14,2),
  interest_component numeric(14,2),
  transaction_id uuid references public.transactions(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (loan_id, installment_number)
);
alter table public.loan_installments enable row level security;
create policy "loan_installments own" on public.loan_installments for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.loan_payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  loan_id uuid not null references public.loans(id) on delete cascade,
  installment_id uuid references public.loan_installments(id) on delete set null,
  transaction_id uuid references public.transactions(id) on delete set null,
  payment_date date not null,
  amount numeric(14,2) not null check (amount > 0),
  notes text,
  created_at timestamptz not null default now()
);
alter table public.loan_payments enable row level security;
create policy "loan_payments own" on public.loan_payments for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.recurring_expenses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  category_id uuid references public.categories(id) on delete set null,
  expected_amount numeric(14,2) not null,
  frequency text not null check (frequency in ('daily','weekly','monthly','quarterly','yearly','custom')),
  first_due_date date not null,
  end_date date,
  payment_account_id uuid references public.accounts(id) on delete set null,
  status text not null default 'active' check (status in ('active','paused','archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.recurring_expenses enable row level security;
create policy "recurring_expenses own" on public.recurring_expenses for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.recurring_occurrences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  recurring_expense_id uuid not null references public.recurring_expenses(id) on delete cascade,
  due_date date not null,
  expected_amount numeric(14,2) not null,
  status text not null default 'expected' check (status in ('expected','paid','skipped','cancelled','rescheduled')),
  transaction_id uuid references public.transactions(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (recurring_expense_id, due_date)
);
alter table public.recurring_occurrences enable row level security;
create policy "recurring_occurrences own" on public.recurring_occurrences for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.budgets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category_id uuid references public.categories(id) on delete set null,
  amount numeric(14,2) not null,
  period_type text not null default 'monthly' check (period_type in ('monthly','custom')),
  period_start date not null,
  period_end date not null,
  rollover boolean not null default false,
  alert_threshold numeric(5,2) default 80,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.budgets enable row level security;
create policy "budgets own" on public.budgets for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.budget_periods (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  budget_id uuid not null references public.budgets(id) on delete cascade,
  period_start date not null,
  period_end date not null,
  budget_amount numeric(14,2) not null,
  actual_amount numeric(14,2) not null default 0,
  created_at timestamptz not null default now(),
  unique (budget_id, period_start, period_end)
);
alter table public.budget_periods enable row level security;
create policy "budget_periods own" on public.budget_periods for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.savings_goals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  goal_type text not null default 'general',
  target_amount numeric(14,2) not null,
  start_date date,
  target_date date,
  starting_balance numeric(14,2) not null default 0,
  linked_account_id uuid references public.accounts(id) on delete set null,
  status text not null default 'active' check (status in ('active','completed','paused','archived')),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.savings_goals enable row level security;
create policy "savings_goals own" on public.savings_goals for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.goal_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  goal_id uuid not null references public.savings_goals(id) on delete cascade,
  event_type text not null check (event_type in ('contribution','withdrawal','adjustment')),
  amount numeric(14,2) not null check (amount > 0),
  event_date date not null,
  account_id uuid references public.accounts(id) on delete set null,
  transaction_id uuid references public.transactions(id) on delete set null,
  notes text,
  created_at timestamptz not null default now()
);
alter table public.goal_events enable row level security;
create policy "goal_events own" on public.goal_events for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.gold_holdings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  purchase_date date not null,
  grams numeric(14,4) not null,
  purity text,
  price_per_gram numeric(14,2),
  making_charges numeric(14,2) default 0,
  gst numeric(14,2) default 0,
  total_cost numeric(14,2) not null,
  seller text,
  notes text,
  created_at timestamptz not null default now()
);
alter table public.gold_holdings enable row level security;
create policy "gold_holdings own" on public.gold_holdings for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.income_allocations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  income_source_id uuid references public.income_sources(id) on delete set null,
  transaction_id uuid references public.transactions(id) on delete set null,
  purpose text not null,
  amount numeric(14,2) not null,
  period_start date,
  period_end date,
  created_at timestamptz not null default now()
);
alter table public.income_allocations enable row level security;
create policy "income_allocations own" on public.income_allocations for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  notification_type text not null,
  title text not null,
  body text,
  status text not null default 'pending' check (status in ('pending','sent','failed','read')),
  dedup_key text,
  scheduled_for timestamptz,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  unique (user_id, dedup_key)
);
alter table public.notifications enable row level security;
create policy "notifications own" on public.notifications for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.import_batches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source text not null,
  row_count int not null default 0,
  status text not null default 'completed',
  created_at timestamptz not null default now()
);
alter table public.import_batches enable row level security;
create policy "import_batches own" on public.import_batches for all to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  entity_type text not null,
  entity_id uuid,
  action text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
alter table public.audit_logs enable row level security;
create policy "audit_logs own read" on public.audit_logs for select to authenticated using (auth.uid() = user_id);
create policy "audit_logs insert" on public.audit_logs for insert to authenticated with check (auth.uid() = user_id);
