-- System categories shared by every user (user_id is null).
-- Written to be safe to re-run: no unique constraint exists on (user_id, name).
insert into public.categories (user_id, name, is_system)
select null, v.name, true
from (
  values
    ('Housing/rent'), ('Groceries'), ('Utilities'), ('Transport'),
    ('Dining'), ('Shopping'), ('Health'), ('Education'),
    ('Insurance'), ('Subscriptions'), ('Travel'), ('Loan interest/fees'),
    ('Personal'), ('Other')
) as v(name)
where not exists (
  select 1 from public.categories c
  where c.user_id is null and c.name = v.name
);
