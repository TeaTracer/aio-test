REVOKE ALL ON SCHEMA public FROM public;

CREATE SCHEMA aio;

CREATE TABLE aio.local_managers (
	id                   serial  NOT NULL,
	first_name           varchar(100)  NOT NULL,
	second_name          varchar(100)  NOT NULL,
	hired_at             date  NOT NULL,
	fired_at             date  ,
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
	init_id              integer  NOT NULL,
	previous_id          integer  ,
	name                 varchar(100)  NOT NULL,
	discription          text  NOT NULL,
	price                numeric(2,12)  NOT NULL,
	category_id          integer  NOT NULL,
	tree_id              integer  NOT NULL,
	changed_at           timestamp DEFAULT current_timestamp NOT NULL,
	changed_by           integer  NOT NULL,
	CONSTRAINT pk_dishes PRIMARY KEY ( id ),
	CONSTRAINT fk_dishes FOREIGN KEY ( changed_by ) REFERENCES aio.local_managers( id )    ,
	CONSTRAINT fk_dishes_0 FOREIGN KEY ( category_id ) REFERENCES aio.categories( id )    ,
	CONSTRAINT fk_dishes_1 FOREIGN KEY ( tree_id ) REFERENCES aio.trees( id )
 );

CREATE INDEX idx_dishes ON aio.dishes ( changed_by );

CREATE INDEX idx_dishes_0 ON aio.dishes ( category_id );

CREATE INDEX idx_dishes_1 ON aio.dishes ( tree_id );

CREATE TABLE aio.menu (
	dish_id              integer NOT NULL,
	inserted_at          timestamp  NOT NULL,
	inserted_by          integer  NOT NULL,
	CONSTRAINT pk_menu PRIMARY KEY ( dish_id ),
	CONSTRAINT fk_menu FOREIGN KEY ( dish_id ) REFERENCES aio.dishes( id )    ,
	CONSTRAINT fk_menu_0 FOREIGN KEY ( inserted_by ) REFERENCES aio.local_managers( id )
 );

CREATE INDEX idx_menu ON aio.menu ( inserted_by );

CREATE TABLE aio.remote_managers (
	id                   serial  NOT NULL,
	first_name           varchar(100)  NOT NULL,
	second_name          varchar(100)  NOT NULL,
	hired_at             date  NOT NULL,
	fired_at             date  ,
	restaurant_id        integer  NOT NULL,
	CONSTRAINT pk_remote_managers PRIMARY KEY ( id ),
	CONSTRAINT fk_remote_managers FOREIGN KEY ( restaurant_id ) REFERENCES aio.restaurants( id )
 );

CREATE INDEX idx_remote_managers ON aio.remote_managers ( restaurant_id );

CREATE TABLE aio.orders (
	id                   serial  NOT NULL,
	manager              integer  NOT NULL,
	tree                 integer  NOT NULL,
	ordered_at           timestamp  NOT NULL,
	order_content        json  NOT NULL,
	CONSTRAINT pk_orders PRIMARY KEY ( id ),
	CONSTRAINT fk_orders FOREIGN KEY ( manager ) REFERENCES aio.remote_managers( id )    ,
	CONSTRAINT fk_orders_0 FOREIGN KEY ( tree ) REFERENCES aio.trees( id )
 );

CREATE INDEX idx_orders ON aio.orders ( manager );

CREATE INDEX idx_orders_0 ON aio.orders ( tree );
