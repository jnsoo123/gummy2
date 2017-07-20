drop table if exists locales;

create table locales (
  id integer primary key autoincrement,
  name text not null,
  code text not null
);
