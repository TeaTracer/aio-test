REVOKE ALL ON SCHEMA public FROM public;
CREATE SCHEMA aio;

CREATE TABLE aio.local_managers (
	id                   serial  NOT NULL,
	name                 varchar(100)  NOT NULL,
	CONSTRAINT pk_local_managers PRIMARY KEY ( id )
 );

CREATE TABLE aio.restaurants (
	id                   serial  NOT NULL,
	name                 varchar(100)  NOT NULL,
	CONSTRAINT pk_restaurants PRIMARY KEY ( id )
 );

CREATE TABLE aio.trees (
	id                   serial  NOT NULL,
	tree                 json  NOT NULL,
	changed_at           timestamp DEFAULT current_timestamp NOT NULL,
	changed_by           integer  NOT NULL,
	CONSTRAINT pk_category_trees PRIMARY KEY ( id ),
	CONSTRAINT fk_category_trees FOREIGN KEY ( changed_by ) REFERENCES aio.local_managers( id )
 );

CREATE INDEX idx_category_trees ON aio.trees ( changed_by );

CREATE TABLE aio.categories (
	id                   serial  NOT NULL,
	name                 varchar(100)  NOT NULL,
	changed_at           timestamp DEFAULT current_timestamp NOT NULL,
	changed_by           integer  NOT NULL,
	CONSTRAINT pk_categories PRIMARY KEY ( id ),
	CONSTRAINT fk_categories FOREIGN KEY ( changed_by ) REFERENCES aio.local_managers( id )
 );

CREATE INDEX idx_categories ON aio.categories ( changed_by );

CREATE TABLE aio.dishes (
	id                   serial  NOT NULL,
	init                 integer  NOT NULL,
	previous             integer  ,
	name                 varchar(100)  NOT NULL,
	discription          text  NOT NULL,
	price                numeric(10,2)  NOT NULL,
	category             integer  NOT NULL,
	tree                 integer  NOT NULL,
	changed_at           timestamp DEFAULT current_timestamp NOT NULL,
	changed_by           integer  NOT NULL,
	CONSTRAINT pk_dishes PRIMARY KEY ( id ),
	CONSTRAINT fk_dishes FOREIGN KEY ( changed_by ) REFERENCES aio.local_managers( id )    ,
	CONSTRAINT fk_dishes_0 FOREIGN KEY ( category ) REFERENCES aio.categories( id )    ,
	CONSTRAINT fk_dishes_1 FOREIGN KEY ( tree ) REFERENCES aio.trees( id )
 );

CREATE INDEX idx_dishes ON aio.dishes ( changed_by );

CREATE INDEX idx_dishes_0 ON aio.dishes ( category );

CREATE INDEX idx_dishes_1 ON aio.dishes ( tree );

CREATE TABLE aio.menu (
	dish                 integer  NOT NULL,
	inserted_at          timestamp  NOT NULL,
	inserted_by          integer  NOT NULL,
	CONSTRAINT pk_menu PRIMARY KEY ( dish ),
	CONSTRAINT fk_menu FOREIGN KEY ( dish ) REFERENCES aio.dishes( id )    ,
	CONSTRAINT fk_menu_0 FOREIGN KEY ( inserted_by ) REFERENCES aio.local_managers( id )
 );

CREATE INDEX idx_menu ON aio.menu ( inserted_by );

CREATE TABLE aio.remote_managers (
	id                   serial  NOT NULL,
	name                 varchar(100)  NOT NULL,
	restaurant           integer  NOT NULL,
	CONSTRAINT pk_remote_managers PRIMARY KEY ( id ),
	CONSTRAINT fk_remote_managers FOREIGN KEY ( restaurant ) REFERENCES aio.restaurants( id )
 );

CREATE INDEX idx_remote_managers ON aio.remote_managers ( restaurant );

CREATE TABLE aio.orders (
	id                   serial  NOT NULL,
	manager              integer  NOT NULL,
	tree                 integer  NOT NULL,
	ordered_at           timestamp  NOT NULL,
	content              json  NOT NULL,
	CONSTRAINT pk_orders PRIMARY KEY ( id ),
	CONSTRAINT fk_orders FOREIGN KEY ( manager ) REFERENCES aio.remote_managers( id )    ,
	CONSTRAINT fk_orders_0 FOREIGN KEY ( tree ) REFERENCES aio.trees( id )
 );

CREATE INDEX idx_orders ON aio.orders ( manager );

CREATE INDEX idx_orders_0 ON aio.orders ( tree );
