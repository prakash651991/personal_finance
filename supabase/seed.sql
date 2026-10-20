insert into public.categories (user_id,name,is_system) values
(null,'Housing/rent',true),(null,'Groceries',true),(null,'Utilities',true),(null,'Transport',true),
(null,'Dining',true),(null,'Shopping',true),(null,'Health',true),(null,'Education',true),
(null,'Insurance',true),(null,'Subscriptions',true),(null,'Travel',true),(null,'Loan interest/fees',true),
(null,'Personal',true),(null,'Other',true)
on conflict do nothing;
