# Personal Finance Management App --- Complete Product & Technical Specification

**Document version:** 1.0\
**Date:** 20 October 2026\
**Status:** Implementation-ready baseline; regulatory review required
before public launch\
**Primary market:** India\
**Currency:** INR (₹)\
**Architecture:** React + TypeScript on Vercel, Supabase (PostgreSQL +
Auth), Python/FastAPI on Google Cloud Run

------------------------------------------------------------------------

## 1. Executive summary

Build a secure, India-focused personal finance application that gives an
individual a consolidated view of income, spending, bank/cash balances,
credit card statements and liabilities, loans and EMIs, recurring
expenses, budgets, savings goals, and gold holdings.

The first release is a **manual-entry personal finance tracker** with
CSV import/export. It does not connect to bank accounts automatically,
initiate payments, issue loans, or make regulated lending decisions.

The central design principle is **one financial ledger, multiple
views**. A purchase, card bill payment, bank transfer, loan EMI, savings
contribution, and refund must each have clear accounting semantics so
the same money movement is not counted twice.

### Product outcomes

1.  Explain where money came from and where it went.
2.  Distinguish purchase/expense date from cash payment date and
    credit-card statement/payment date.
3.  Track multiple credit cards with independent statement cycles and
    due dates.
4.  Track multiple income sources and planned allocation of income.
5.  Create reusable monthly expenses and category budgets.
6.  Track loans by start date, end date, EMI amount, due date, schedule,
    and payment history.
7.  Track goals over a time period, including a gold savings goal and
    optional physical gold holdings.
8.  Present reliable dashboards, reminders, reports, and exports.
9.  Protect every user's financial records with strong authorization and
    privacy controls.

------------------------------------------------------------------------

## 2. Scope and non-goals

### 2.1 In scope for MVP

-   User registration, login, logout, password recovery, profile and
    preferences.
-   Accounts: bank accounts, cash wallets and savings accounts.
-   Income sources and income records.
-   Transactions: expenses, income, refunds, transfers, adjustments and
    repayments.
-   Categories, subcategories, notes, tags, search and filtering.
-   Multiple credit cards, independent billing rules, statements,
    unbilled transactions, due dates and card payments.
-   Fixed/recurring monthly expenses and reusable budgets.
-   Loans, scheduled EMIs, payment tracking, partial payments and
    overdue status.
-   Savings goals, dated contributions and withdrawals.
-   Gold savings goal; optional actual gold holding records.
-   Dashboard, calendar, category analysis, cash-flow reports and
    upcoming obligations.
-   CSV import/export, backup/restore process, audit trail and account
    deletion workflow.
-   Email/in-app reminders; push/SMS can be added later.

### 2.2 Out of scope for MVP

-   Automatic bank/card data aggregation.
-   Initiating payments or moving customer money.
-   Lending, loan brokering, underwriting or credit decisions.
-   Storing card PIN, CVV, OTP, internet-banking password or other
    payment credentials.
-   Investment execution, brokerage, or guaranteed gold-market
    valuation.
-   Shared household accounts and multi-user budgets (possible later
    phase).
-   Tax advice or guarantees that a dashboard category is
    tax-deductible.

### 2.3 User roles

-   **Unauthenticated visitor:** Can access public landing/help pages
    only.
-   **Authenticated user:** Can access and manage their own records.
-   **Support/operator:** No routine access to financial content. Any
    exceptional support access must be time-limited, authorized, logged
    and disclosed as appropriate.
-   **System job:** Performs only narrowly scoped scheduled work; must
    not have unrestricted access to all user data where avoidable.

------------------------------------------------------------------------

## 3. System architecture

``` mermaid
flowchart TD
    U[User: mobile or desktop browser] --> V[Vercel: React + TypeScript]
    V --> A[Supabase Auth]
    V -->|HTTPS API with access token| C[Cloud Run: FastAPI]
    C -->|Validate user JWT / authorized database access| S[Supabase PostgreSQL]
    C --> N[Notification provider]
    C --> O[Observability and error reporting]
    J[Cloud Scheduler] -->|Authenticated scheduled request| C
    S --> R[Backup and restore process]
    G[GitHub repository] --> V
    G --> D[Cloud Run deployment pipeline]
```

### 3.1 Vercel frontend

Responsibilities: - Render responsive web UI. - Provide accessible
forms, tables, charts and calendars. - Use Supabase Auth for
sign-in/session handling. - Call backend endpoints for business
operations. - Display server-validated calculations; do not make client
calculations the financial source of truth. - Never expose Supabase
service-role keys, database passwords, Cloud Run privileged credentials
or notification-provider secrets.

Recommended stack: - React + TypeScript. - Vite or a supported React
framework. - Tailwind CSS or equivalent design system. - React Hook
Form + schema validation. - Recharts or equivalent chart library. -
Playwright for end-to-end tests.

### 3.2 Supabase

Responsibilities: - PostgreSQL as the system of record. - Supabase
Auth. - Row Level Security (RLS) on every user-owned table. - Database
constraints, indexes and migrations. - Optional private object storage
for user-uploaded statements/receipts, only if needed.

Use Supabase CLI migrations committed to source control. Do not make
undocumented production schema edits through the dashboard.

### 3.3 Google Cloud Run backend

Responsibilities: - FastAPI REST API. - Credit-card statement assignment
logic. - EMI schedule generation and payment reconciliation. -
Transaction validation and duplicate detection. - Dashboard/report
calculations. - CSV import validation. - Scheduled reminders and
periodic status reconciliation. - Audit events and structured logs.

Use a modular monolith initially. Modules can be separated in code
without creating multiple microservices.

Suggested Python modules:

``` text
app/
  main.py
  api/
    auth.py
    accounts.py
    transactions.py
    income.py
    credit_cards.py
    statements.py
    loans.py
    budgets.py
    recurring_expenses.py
    goals.py
    gold.py
    reports.py
    notifications.py
  domain/
    ledger.py
    card_billing.py
    loan_schedule.py
    budgets.py
    goal_tracking.py
    cash_flow.py
  repositories/
  schemas/
  services/
  jobs/
  security/
  tests/
```

### 3.4 Authentication flow

1.  User signs in through Supabase Auth.
2.  Frontend obtains a short-lived access token.
3.  Frontend sends the token as `Authorization: Bearer <token>` to Cloud
    Run.
4.  Backend validates signature, issuer, audience, expiry and subject
    against the configured Supabase project.
5.  Backend derives the user ID from the validated token, never from an
    untrusted request body.
6.  Every database operation is scoped to that user, and RLS remains an
    independent security layer.
7.  Never accept a client-supplied `user_id` as proof of ownership.

Prefer user-scoped database access or carefully designed database
functions. If a privileged service credential is used, the API must
enforce ownership in every query and mutation; RLS bypass must not
become the only protection.

### 3.5 Deployment environments

Maintain separate development, staging and production environments: -
Separate Supabase projects or isolated databases. - Separate Vercel
environment variables. - Separate Cloud Run services and service
accounts. - Synthetic data in development/staging. - Database migrations
applied through CI/CD with review and rollback plan. - No production
financial data in test fixtures or logs.

------------------------------------------------------------------------

## 4. Core domain model and accounting rules

### 4.1 Transaction types

Use explicit types such as: - `income` - `expense` - `refund` -
`transfer` - `credit_card_purchase` - `credit_card_payment` -
`loan_disbursement` - `loan_repayment` - `savings_contribution` -
`savings_withdrawal` - `adjustment`

The app may present simpler labels to users, but backend logic must
preserve the semantic type.

### 4.2 One source of truth

Each real-world movement must be recorded once in the ledger. Other
features should link to that record rather than create another
independent expense.

Examples: - Card purchase: counts as spending once and increases card
liability. - Credit card bill payment: cash outflow and liability
settlement; not a second purchase expense. - Bank-to-bank transfer:
movement between owned accounts; not income or expense. -
Savings-account transfer: transfer, not consumption spending. - Savings
goal contribution: goal allocation/event; not an additional expense if
the underlying transfer is already recorded. - Loan EMI: cash outflow
and loan settlement. If principal/interest split is known, principal
reduces liability and interest is an expense. If unknown, label the
split as unknown instead of inventing it. - Refund: linked to the
original purchase where possible; retain both records and report net
spending according to a documented date policy.

### 4.3 Money and dates

-   Store monetary values as PostgreSQL `NUMERIC(14,2)` or integer
    paise; never use binary floating-point for money.
-   Store dates as `DATE` for purchase, due and statement dates.
-   Store timestamps as `TIMESTAMPTZ` for audit events.
-   Use `Asia/Kolkata` for user-facing date/time behavior by default,
    configurable where appropriate.
-   Store currency as ISO code, default `INR`.
-   Define rounding rules centrally and test them.
-   Do not derive transaction dates from server UTC dates without
    applying the user's configured timezone.

### 4.4 Historical integrity

-   Posted transactions and issued statements must not silently change
    when a user edits a recurring template or future billing rule.
-   Corrections to settled records should use an explicit
    reversal/adjustment workflow.
-   Financial changes should be auditable.
-   Deleting a card or loan with history should normally archive it
    rather than erase its history.

------------------------------------------------------------------------

## 5. Functional requirements

## 5.1 User profile and settings

Fields: - Display name (optional). - Email/auth identity managed by
Supabase Auth. - Default currency: INR. - Timezone: Asia/Kolkata by
default. - Start day for custom budget period (default calendar
month). - Notification preferences. - Default dashboard date range.

Functions: - Sign up/sign in/sign out/password reset. - Update
preferences. - Export data. - Request account deletion. - Review privacy
notice and consent records where applicable.

## 5.2 Accounts

Account types: - Bank account. - Cash wallet. - Savings account. - Other
manually tracked asset account (optional).

Fields: - Name/nickname. - Institution (optional). - Account type. -
Opening balance and effective date. - Current calculated balance. -
Active/archived status.

Logic: - Account balance = opening balance + posted inflows − posted
outflows, using defined transfer/transaction semantics. - Opening
balances must not be counted as new income. - Transfers must create
linked outflow/inflow entries atomically. - Reconciliation allows a user
to compare calculated balance with the balance shown by their bank. -
Never store online banking credentials.

## 5.3 Income streams

Examples: salary, freelance, business, rent received, interest and other
income.

Fields: - Source name/type. - Amount. - Received date. - Destination
account. - Recurrence rule (optional). - Notes and category.

Features: - Multiple income sources. - Monthly and custom-period totals
by source. - Expected versus received income. - Income source CRUD. -
Planned allocations to bills, goals and other purposes.

Allocation logic: - An allocation is a plan, not proof of a
transaction. - Show planned, actual and unallocated amounts
separately. - Warn if planned allocations exceed the selected income or
available cash. - When an actual expense or transfer is linked to an
allocation, do not subtract it a second time from cash balance.

## 5.4 Transactions

Fields: - Transaction ID, owner ID, type, amount, currency. -
Transaction/purchase date and optional posting date. - Account/card
reference. - Category/subcategory. - Merchant/description, notes,
tags. - Linked transfer group, linked refund/original transaction,
linked statement or loan installment. - Status: draft, posted, reversed
or archived where appropriate. - Created/updated timestamps.

Features: - Create, view, edit and delete eligible transactions. -
Search, sort, filter, paginate. - Recurring transaction templates. -
Receipt attachment (optional; private storage). - CSV import/export. -
Duplicate detection and reconciliation.

Validation: - Amount must be positive; direction comes from type. -
Account/card must belong to authenticated user. - Transaction date
cannot be invalid. - A transfer must have valid source and destination
accounts and cannot transfer to the same account. - Reject or flag
duplicate import fingerprints. - For settled transactions, use
reversal/adjustment rather than silent destructive editing.

## 5.5 Categories and budgets

Default categories may include: - Housing/rent - Groceries - Utilities -
Transport - Dining - Shopping - Health - Education - Insurance -
Subscriptions - Travel - Loan interest/fees - Personal - Other

Users can create custom categories and subcategories.

Budget fields: - Category. - Amount. - Period type. - Start/end or
effective period. - Rollover policy (default off). - Alert threshold. -
Active status.

Logic: - Actual category spending = posted eligible expenses minus
applicable refunds under the chosen reporting-date policy. - Exclude
transfers, card bill settlements, goal allocations and loan principal
repayments from consumption spending. - If loan interest is known,
include the interest component in expense reports. - Budget remaining =
budget amount − actual eligible spending. - Negative remaining means
over budget. - Budget templates can repeat monthly, but historical
budget snapshots must remain stable. - Budget edits should specify
whether they apply to future periods only or also revise the current
period.

## 5.6 Recurring/fixed expenses

Examples: rent, school fees, internet, insurance, subscriptions and
recurring loan obligations.

Fields: - Name/category. - Expected amount. - Frequency. - First due
date. - Optional end date. - Account/payment method. -
Active/paused/archived state. - Adjustment/effective date.

Logic: - Generate expected occurrences idempotently. - Expected
occurrences are not actual expenses until paid/confirmed. - Link a paid
occurrence to the actual transaction. - Do not generate duplicate
occurrences if a scheduled job retries. - Editing a template affects
future occurrences unless the user explicitly chooses otherwise. -
Support skipped, cancelled and rescheduled occurrences with an audit
trail.

## 5.7 Credit cards and billing cycles

Fields: - Card nickname and issuer. - Optional last four digits only; do
not store CVV/PIN/OTP. - Credit limit. - Statement generation/cut-off
date. - Due-day rule or actual due date from statement. - Billing cycle
rule. - Active/archived state.

### Billing terminology

-   **Purchase date:** Date user bought the item.
-   **Posting date:** Date transaction was posted by the issuer, if
    known.
-   **Statement period:** Period included on a particular statement.
-   **Statement date:** Date statement was generated.
-   **Payment due date:** Actual due date shown by issuer.
-   **Unbilled amount:** Eligible card activity not assigned to an
    issued statement.
-   **Outstanding liability:** Amount still owed, considering posted
    purchases, fees, interest, refunds and payments.

### Standard cycle behavior

For a card with statement date on the 20th, a purchase on October 10
will normally appear on the October 20 statement, subject to issuer
posting and cut-off rules; payment may be due in November. A purchase
after the cut-off generally belongs to the next statement. The app must
distinguish **spending month** from **payment month**.

Do not assume every issuer uses identical rules. Allow the user to
configure the rule, and let the user override a statement assignment
where needed.

### Statement assignment logic

1.  Determine the expected statement period from that card's configured
    cut-off rule.
2.  Prefer the issuer's actual posting date when supplied by the user.
3.  Assign only eligible transactions to an open/future statement.
4.  Preserve the assigned statement once issued.
5.  Record the statement's total, minimum due if known, due date, and
    payment status.
6.  Allow manual correction with an audit entry.
7.  Never claim an estimated date/amount is an issuer-confirmed
    statement.

### Credit card payments

-   Payment reduces bank/cash balance and card liability.
-   Payment does not create another purchase expense.
-   Support full, partial and multiple payments.
-   Link a payment to a statement or card balance.
-   Prevent duplicate payment imports.
-   Show billed balance, unbilled activity, total liability, available
    credit estimate and due dates separately.
-   Mark available credit as an estimate when issuer data is not
    connected.

## 5.8 Loan tracking and EMI management

The user must be able to add loans with: - Loan name/type. - Lender name
(optional). - Start date. - End date. - Monthly EMI amount. - EMI due
day and first EMI date (recommended). - Original principal (optional). -
Interest rate and interest type (optional). - Linked bank account
(optional). - Loan status and notes.

### Loan schedule logic

1.  Validate end date is on/after start date and EMI is positive.
2.  If a first EMI date is supplied, use it as the first installment
    date. Otherwise ask the user to confirm a default.
3.  Generate monthly installment dates through the end date, subject to
    a confirmed lender schedule.
4.  If due day is 29--31 and a month is shorter, clamp to that month's
    final calendar day unless the user configures a different rule.
5.  Store installment number, due date, expected amount, paid amount,
    status and transaction link.
6.  Use a uniqueness constraint on `(loan_id, installment_number)` and
    an idempotent generation process.
7.  Record partial and full payments without overwriting payment
    history.
8.  Reconcile scheduled/paid/overdue statuses on read or via an
    idempotent scheduled job.
9.  When the loan terms change, preview the new future schedule;
    preserve paid installments and audit the change.
10. Archive loans with payment history instead of destructively deleting
    them.

### What can be calculated

With start date, end date and EMI: - Estimated number of installments,
if the first EMI date/rule is defined. - Total scheduled repayments =
installment count × EMI, adjusted for any explicitly configured final
installment.

These values do **not** prove the original principal, current principal
outstanding or interest paid. Those require additional loan terms, a
lender schedule, or manually entered balance data.

### Loan principal and interest

-   If principal/interest components are provided, record them per
    installment.
-   Principal reduces loan liability.
-   Interest is a cost/expense.
-   If the split is unknown, show it as unknown; do not invent an
    amortization schedule.
-   For a basic tracker, the full EMI is a cash outflow and loan
    repayment, while expense reporting must clearly distinguish unknown
    interest/principal allocation.
-   Support extra repayments and foreclosure only with explicit user
    entries and an audit trail.

### Loan dashboard

Display: - Active loans. - EMI due next and due date. - Total monthly
EMI commitments. - Paid, partial, upcoming and overdue installments. -
Scheduled repayments remaining. - Principal outstanding only when
sufficient data exists. - Payment history and downloadable report.

## 5.9 Savings goals

Goal fields: - Name/type. - Target amount. - Start date and target
date. - Starting balance (optional). - Linked account (optional). -
Status. - Notes.

Goal types: emergency fund, gold, home, vehicle, education, travel,
general and custom.

Logic: - Remaining target = max(target amount − goal balance, 0). -
Monthly target uses remaining target and the number of contribution
periods remaining; display assumptions clearly. - Contributions and
withdrawals are separate events. - A goal balance may be earmarked money
already included in a bank account balance; never add it twice to total
assets. - Mark completed only when the user confirms or the goal reaches
its target according to the selected rule. - Allow date and target edits
with historical contribution preservation.

## 5.10 Gold tracking

Two modes:

**Gold savings goal:** Track cash accumulated for a future gold
purchase, contribution dates and target date.

**Physical gold holdings:** Optional records for purchase date, grams,
purity, price per gram, making charges, GST, total cost, seller and
notes.

Logic: - Do not treat a cash savings goal as already-owned gold. -
Record actual gold purchase separately from the cash contribution. - If
market valuation is later supported, store valuation timestamp, price
source, purity and calculation assumptions. - Display estimated value
separately from cost; do not imply it is a guaranteed sale price. -
Avoid automatic gold price claims without a reliable data provider and
explicit source/date.

## 5.11 Dashboard and reports

Dashboard metrics: - Income received in selected period. - Eligible
actual spending. - Net cash flow. - Bank/cash balances. - Credit card
billed/unbilled liability. - Upcoming card payments. - Total monthly
loan EMI commitments. - Upcoming loan installments. - Budget remaining
and overspend. - Savings-goal progress. - Unallocated planned income. -
Net worth, only where tracked assets and liabilities are sufficiently
complete.

Filters: - Calendar month/custom range. - Card billing period. -
Account/card. - Income source. - Category. - Cash-flow view versus
consumption-spending view. - Planned versus actual. - Goal/loan.

Reports: - Income by source. - Spending by category and merchant. -
Monthly cash flow. - Budget versus actual. - Card statements and
payments. - Loan schedule and repayment history. - Goal contributions. -
Account reconciliation. - CSV export.

Every metric must have a documented definition and date basis. The UI
should explain whether a chart uses purchase date, posting date,
statement date, due date or payment date.

## 5.12 Notifications

MVP notification types: - Credit card due soon/overdue. - EMI due
soon/overdue. - Recurring bill approaching. - Budget threshold
exceeded. - Goal target date approaching. - Import/reconciliation
warnings.

Logic: - User controls notification preferences and lead time. -
Scheduled jobs are idempotent. - Avoid sending duplicate notifications
for the same event and reminder window. - Do not include sensitive
financial details in lock-screen/email subject lines unless the user
opts in. - A reminder is not proof of payment. - Notification failure
must not alter ledger records.

------------------------------------------------------------------------

## 6. Database design

Use Supabase PostgreSQL with migrations. Every user-owned table should
include `user_id` or have a safe ownership relationship that can be
enforced by RLS.

### 6.1 Main tables

  Table                        Purpose
  ---------------------------- --------------------------------------------
  `profiles`                   User preferences and profile
  `accounts`                   Bank/cash/savings accounts
  `income_sources`             Income categories/sources
  `transactions`               Canonical financial activity
  `categories`                 System and user-defined categories
  `recurring_expenses`         Recurring templates
  `recurring_occurrences`      Expected bill instances
  `budgets`                    Budget definitions/templates
  `budget_periods`             Period snapshots
  `credit_cards`               Card configuration
  `credit_card_statements`     Issued/estimated statement periods
  `credit_card_transactions`   Card purchase/fee/refund details
  `credit_card_payments`       Card payment allocations
  `loans`                      Loan metadata and user-entered terms
  `loan_installments`          Scheduled EMI rows
  `loan_payments`              Actual EMI/extra payment history
  `savings_goals`              Goal definitions
  `goal_events`                Contributions, withdrawals and adjustments
  `gold_holdings`              Physical gold purchase records
  `income_allocations`         Planned use of income
  `notifications`              Reminder delivery state
  `import_batches`             CSV import runs
  `audit_logs`                 Important mutations and corrections

### 6.2 Example transaction schema

``` sql
CREATE TABLE public.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    account_id UUID,
    transaction_type TEXT NOT NULL CHECK (
      transaction_type IN (
        'income','expense','refund','transfer',
        'credit_card_purchase','credit_card_payment',
        'loan_disbursement','loan_repayment',
        'savings_contribution','savings_withdrawal','adjustment'
      )
    ),
    amount NUMERIC(14,2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    transaction_date DATE NOT NULL,
    posting_date DATE,
    category_id UUID,
    income_source_id UUID,
    description TEXT,
    notes TEXT,
    transfer_group_id UUID,
    linked_transaction_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_user_date
  ON public.transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_user_type_date
  ON public.transactions(user_id, transaction_type, transaction_date DESC);

ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users access own transactions"
ON public.transactions FOR ALL TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

This is a starting example, not the complete production migration. Add
foreign keys for account/category/income-source references, validate
ownership across related tables, and design transfer/payment operations
transactionally.

### 6.3 Credit-card tables

`credit_cards` should store owner, nickname, issuer, last four digits
(optional), limit, statement-day rule, cycle configuration, due-day
preference and status.

`credit_card_statements` should store card, period start/end, statement
date, actual/estimated status, statement total, minimum due if known,
actual due date, paid amount and status.

`credit_card_transactions` should store card, linked canonical
transaction, purchase date, posting date, statement ID, transaction kind
and issuer/reference metadata where provided.

`credit_card_payments` should store card, linked cash transaction,
payment date, amount and statement allocation. A payment may be
allocated to more than one statement if needed.

Use uniqueness constraints for imported issuer references where
available, and preserve manual overrides.

### 6.4 Loan tables

`loans`: - `id`, `user_id`, `name`, `lender_name`. - `start_date`,
`end_date`, `first_emi_date`, `emi_due_day`. - `emi_amount`, optional
`original_principal`, optional `annual_interest_rate`. - Optional
payment account, status, notes and timestamps.

`loan_installments`: - `id`, `loan_id`, `user_id`, installment number,
due date. - Expected amount, paid amount, paid date, status. - Optional
principal/interest components and linked transaction. - Unique
`(loan_id, installment_number)`.

`loan_payments`: - `id`, `loan_id`, `installment_id`, `user_id`. -
Payment date, amount, account/transaction link, notes and timestamps.

Add RLS policies for every table, and ensure a user's
installment/payment cannot reference another user's loan or transaction.
Use composite constraints or trusted database functions where necessary
to enforce same-owner relationships.

### 6.5 Database integrity and deletion

-   Use foreign keys and explicit `ON DELETE` policies.
-   Prefer archive/soft-delete for financial entities with history.
-   Use a database transaction for transfers, card payments, loan
    payments and schedule generation.
-   Use idempotency keys for retryable API operations.
-   Add audit records for material edits, reversals, schedule changes
    and account deletion requests.
-   Avoid putting complete financial descriptions, access tokens or
    sensitive details into operational logs.

------------------------------------------------------------------------

## 7. API design

Base URL: `/api/v1`

Use JSON request/response bodies, standard HTTP status codes,
pagination, schema validation and a consistent error format.

  ------------------------------------------------------------------------------------
  Method                  Endpoint                           Purpose
  ----------------------- ---------------------------------- -------------------------
  `GET`                   `/profile`                         Get preferences

  `PATCH`                 `/profile`                         Update preferences

  `GET/POST`              `/accounts`                        List/create accounts

  `PATCH/DELETE`          `/accounts/{id}`                   Update/archive account

  `GET/POST`              `/transactions`                    List/create transactions

  `GET/PATCH/DELETE`      `/transactions/{id}`               Retrieve/update/reverse
                                                             eligible transaction

  `GET/POST`              `/income-sources`                  List/create income
                                                             sources

  `GET/POST`              `/credit-cards`                    List/create cards

  `GET`                   `/credit-cards/{id}/statements`    List statements

  `GET`                   `/credit-cards/{id}/unbilled`      List unbilled activity

  `POST`                  `/credit-cards/{id}/payments`      Record card payment

  `GET/POST`              `/loans`                           List/create loans

  `GET/PATCH/DELETE`      `/loans/{id}`                      View/update/archive loan

  `GET`                   `/loans/{id}/installments`         List EMI schedule

  `POST`                  `/loans/{id}/payments`             Record payment

  `POST`                  `/loans/{id}/reschedule-preview`   Preview future schedule
                                                             changes

  `POST`                  `/loans/{id}/reschedule`           Confirm reschedule

  `GET/POST`              `/budgets`                         List/create budgets

  `GET/POST`              `/recurring-expenses`              List/create templates

  `GET/POST`              `/savings-goals`                   List/create goals

  `POST`                  `/savings-goals/{id}/events`       Add
                                                             contribution/withdrawal

  `GET`                   `/dashboard/summary`               Consolidated dashboard

  `GET`                   `/reports/cash-flow`               Cash-flow report

  `GET`                   `/reports/spending`                Category spending report

  `POST`                  `/imports/csv`                     Validate/import CSV

  `GET`                   `/exports/transactions`            Export transactions
  ------------------------------------------------------------------------------------

### API requirements

-   Authenticate every private endpoint.
-   Derive user identity from the validated token.
-   Check ownership of every referenced ID.
-   Validate inputs with Pydantic.
-   Use server-side pagination and filter allowlists.
-   Use idempotency keys for payment/import operations.
-   Return `404` for inaccessible resources where that reduces ID
    enumeration.
-   Never return service secrets or unnecessary sensitive fields.
-   Add rate limits for authentication-adjacent and expensive endpoints.
-   Document API contracts in OpenAPI.

Example error shape:

``` json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The requested operation could not be completed.",
    "request_id": "server-generated-correlation-id"
  }
}
```

Do not expose stack traces, SQL, tokens or internal secrets to clients.

------------------------------------------------------------------------

## 8. Financial calculations and canonical definitions

Create a shared domain layer for all financial calculations. Do not
duplicate billing/EMI math in React components.

### 8.1 Cash flow

For a selected period:

`Net cash flow = eligible cash inflows − eligible cash outflows`

Opening balances and internal transfers are excluded from income/expense
totals. Transfers can appear separately in account movement reports.

### 8.2 Consumption spending

`Net spending = eligible posted expenses − linked/applicable refunds`

Exclude: - Internal transfers. - Credit card bill settlements when card
purchases have already been counted. - Savings goal allocations. - Loan
principal repayment. - Opening balance adjustments.

Include interest/fees as expenses when known and appropriately
classified.

### 8.3 Credit-card liability

Track separately: - Statement balance. - Unbilled transactions. -
Payments. - Refunds/credits. - Fees/interest. - Total outstanding
liability.

Do not simply sum all purchases ever recorded. Reconcile against
statements and payments. Clearly label balances as
user-tracked/estimated when no issuer feed exists.

### 8.4 Loan calculations

-   Scheduled installment count depends on first EMI date and confirmed
    monthly schedule, not just inclusive month count.
-   Scheduled total = sum of installment expected amounts.
-   Paid total = sum of successful linked payments.
-   Remaining scheduled amount = scheduled amount remaining, not
    necessarily principal outstanding.
-   Principal outstanding requires a reliable principal schedule/opening
    principal and all principal repayments.
-   Interest paid requires known interest components or a validated
    amortization schedule.
-   Late/overdue status depends on unpaid amount and due date, with a
    defined timezone/date policy.
-   Partial payments remain partial until the installment is fully paid
    or explicitly resolved.
-   Extra payments must not silently alter future installments unless
    the user confirms a reschedule.

### 8.5 Savings and net worth

-   Goal balance = starting balance + contributions − withdrawals ±
    explicitly recorded adjustments.
-   Do not add goal balances on top of account balances if the money is
    already included in those accounts.
-   Net worth = tracked assets − tracked liabilities, only when data
    coverage is sufficient.
-   Display an "incomplete estimate" notice when assets/liabilities are
    missing or estimated.

------------------------------------------------------------------------

## 9. Security, privacy and India regulatory considerations

This section is an engineering baseline, not legal advice.

### 9.1 Security controls

-   TLS for all network traffic.
-   Managed encryption at rest for database/storage.
-   RLS on every user-owned table.
-   Strict server-side authorization on all API operations.
-   No service-role key in browser code or public environment variables.
-   Least-privilege service accounts and secrets management.
-   Dependency and container vulnerability scanning.
-   Rate limiting, secure headers and safe CORS configuration.
-   Audit events for sensitive changes.
-   Redacted structured logs.
-   Encrypted backups and tested restore drills.
-   Account deletion/export workflows.
-   Incident response and security contact process.

### 9.2 Data minimization

For manual tracking, do not collect: - Card PIN, CVV or OTP. -
Internet-banking passwords. - Full card number unless a separately
justified and reviewed use case exists; default to nickname and last
four digits only. - Unnecessary identity or financial documents.

Make privacy notice and data-use purposes understandable. Define
retention periods and subprocessors. Avoid using financial data for
advertising.

### 9.3 RBI scope

A manual personal finance tracker is not automatically a bank, lender or
payment system operator. Regulatory obligations depend on the actual
services, integrations and business model.

Before adding features: - Automatic financial-data retrieval: assess
authorized Account Aggregator or other permitted integration paths and
consent requirements. - Loan referrals/origination: assess RBI digital
lending rules and whether the product is acting for or with a regulated
entity. - Payment initiation or handling funds: obtain specialist
regulatory review. - Credit scoring or decisions for lenders: assess
applicable obligations before release.

Review the current RBI directions, applicable data-protection law/rules
and contractual requirements with qualified Indian counsel before
launch. Do not describe the product as "RBI approved" unless there is a
valid basis for that claim.

------------------------------------------------------------------------

## 10. Testing strategy

### 10.1 Unit tests

Test: - Money rounding and currency formatting. - Credit-card cycle
boundary dates. - Month-end and leap-year due dates. - Statement
assignment and manual override. - Refund handling. - Transfer
neutrality. - Duplicate import detection. - EMI date generation and
installment count. - Partial/full payment transitions. - Schedule
changes preserving paid installments. - Goal balance and progress. -
Budget calculations and period boundaries.

### 10.2 Integration tests

Test: - Supabase RLS with two separate test users. - Every API
endpoint's authentication and ownership enforcement. - Transactional
transfer creation. - Credit card payment and liability update. - Loan
payment and linked transaction creation. - Retry/idempotency behavior. -
CSV import failures and partial-file policy. - Scheduled reminder
deduplication. - Database migration from a clean database.

### 10.3 End-to-end tests

1.  Register and sign in.
2.  Add two bank accounts and a cash wallet.
3.  Add salary and freelance income.
4.  Record expenses and an internal transfer.
5.  Add two credit cards with different statement dates.
6.  Add purchases before and after a statement cut-off.
7.  Generate/view statements and record a partial card payment.
8.  Add a loan, generate EMI schedule and record a payment.
9.  Add a recurring rent expense and mark one occurrence paid.
10. Create a goal and record a contribution.
11. Confirm dashboard totals do not double-count transfers, card
    settlements or goal allocations.
12. Export data and verify ownership isolation.

### 10.4 Acceptance criteria

The release is not complete until: - A user cannot read or modify
another user's records. - All financial totals reconcile with
deterministic test fixtures. - Credit card purchase month and payment
month are shown separately. - Loan schedule assumptions are visible and
editable. - Historical paid installments and issued statements remain
unchanged after future schedule edits. - Repeated requests do not create
duplicate payments or reminders. - A card payment is not counted as a
second purchase expense. - Internal transfers are excluded from income
and consumption spending. - Backups can be restored successfully. - The
app can export user data and process account deletion according to the
defined policy.

------------------------------------------------------------------------

## 11. Observability, operations and cost control

-   Use structured logs with request IDs.
-   Do not log transaction descriptions, account details, access tokens
    or sensitive request bodies.
-   Track API error rate, latency, database connection use, failed
    scheduled jobs and notification failures.
-   Set Cloud Run minimum instances to zero for a cost-sensitive MVP
    unless latency requirements justify otherwise.
-   Use bounded request timeouts and concurrency appropriate to the
    database connection budget.
-   Use connection pooling/appropriate Supabase connection settings.
-   Schedule jobs through Cloud Scheduler or another managed scheduler;
    jobs must be idempotent.
-   Configure alerts for repeated failures and database capacity.
-   Keep a documented incident response and restore procedure.

------------------------------------------------------------------------

## 12. Development roadmap

### Phase 1 --- Foundation

-   Repository, CI/CD and environments.
-   Supabase schema and RLS.
-   Auth, profiles, accounts, categories and transaction CRUD.
-   Basic dashboard and tests.

### Phase 2 --- Credit cards

-   Card CRUD.
-   Statement-cycle engine.
-   Statement records, unbilled transactions, payment reconciliation.
-   Boundary-date tests and statement history.

### Phase 3 --- Loans

-   Loan CRUD.
-   First EMI date and due-day behavior.
-   Schedule generation, payment history, partial payments and overdue
    reminders.
-   Principal/interest support only when data is available.

### Phase 4 --- Budgets and goals

-   Recurring expenses and occurrences.
-   Category budgets and historical snapshots.
-   Income sources and planned allocations.
-   Savings goals and gold tracking.

### Phase 5 --- Reporting

-   Cash flow, spending, liabilities, loan obligations, savings and net
    worth views.
-   Filters, CSV export and dashboard definitions.
-   Reconciliation and consistency checks.

### Phase 6 --- Production readiness

-   Security review and penetration testing appropriate to launch scope.
-   Privacy/legal review.
-   Backups and restore drills.
-   Monitoring, rate limits and incident response.
-   Beta rollout, feedback and defect triage.

------------------------------------------------------------------------

## 13. Recommended repository layout

``` text
personal-finance-app/
  frontend/
    src/
      app/
      components/
      features/
        accounts/
        transactions/
        income/
        credit-cards/
        loans/
        budgets/
        recurring-expenses/
        savings-goals/
        gold/
        dashboard/
      lib/
      tests/
  backend/
    app/
      api/
      domain/
      repositories/
      schemas/
      services/
      jobs/
      security/
      tests/
    Dockerfile
    pyproject.toml
  supabase/
    migrations/
    seed.sql
    config.toml
  docs/
    SYSTEM_DESIGN.md
    API.md
    DATA_MODEL.md
    SECURITY.md
    TEST_PLAN.md
  .github/
    workflows/
  README.md
```

Keep secrets in deployment secret stores and local ignored environment
files. Include `.env.example` with variable names and dummy values only.

------------------------------------------------------------------------

## 14. Definition of done

A feature is complete only when: 1. Its requirements and business rules
are documented. 2. Database migrations and RLS policies are included. 3.
Backend validation and ownership checks are implemented. 4. UI states
cover loading, empty, error and success cases. 5. Financial logic has
unit tests. 6. API behavior has integration tests. 7. Key user journeys
have end-to-end tests. 8. Audit and idempotency requirements are
satisfied. 9. Documentation and API schema are updated. 10. The feature
has been tested in staging with synthetic data.

------------------------------------------------------------------------

## 15. Decisions to confirm during implementation

The architecture and core scope are defined. Resolve these details
before coding each module:

1.  **Credit card cycles:** Default to conventional statement cut-off
    behavior; allow issuer-specific rules and manual overrides.
2.  **Loan first EMI date:** Ask explicitly or clearly label the
    default; do not assume the loan start date is the first due date.
3.  **Loan balance:** Show principal outstanding only when opening
    principal and repayment data support it.
4.  **Budget period:** Calendar month by default; allow a custom start
    day later.
5.  **Transaction deletion:** Reverse/archive settled records; do not
    silently destroy financial history.
6.  **Bank integration:** Keep out of MVP until regulatory, consent,
    security and provider requirements are reviewed.
7.  **Notifications:** Start with in-app/email; add push/SMS only after
    cost and consent requirements are understood.

## Final recommendation

Build this as a modular monolith with **Vercel for the React frontend,
Supabase for authentication and PostgreSQL, and Cloud Run for the
FastAPI financial logic**. Make the canonical ledger and reconciliation
rules the foundation. Implement credit-card billing and loan repayments
before advanced dashboards so all displayed totals are consistent and
auditable.

This document is the product and engineering baseline. It should be
paired with concrete Supabase migrations, OpenAPI contracts, UI designs,
automated tests and an India-specific legal review before public launch.
