--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 9.6.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: gejala; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE gejala (
    id_gejala bigint NOT NULL,
    nama_gejala character varying(50) NOT NULL
);


ALTER TABLE gejala OWNER TO postgres;

--
-- Name: gejala_id_gejala_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE gejala_id_gejala_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE gejala_id_gejala_seq OWNER TO postgres;

--
-- Name: gejala_id_gejala_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE gejala_id_gejala_seq OWNED BY gejala.id_gejala;


--
-- Name: gejala_penyakit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE gejala_penyakit (
    id_gejala_penyakit bigint NOT NULL,
    id_penyakit bigint NOT NULL,
    id_gejala bigint NOT NULL,
    bobot double precision
);


ALTER TABLE gejala_penyakit OWNER TO postgres;

--
-- Name: gejala_penyakit_id_gejala_penyakit_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE gejala_penyakit_id_gejala_penyakit_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE gejala_penyakit_id_gejala_penyakit_seq OWNER TO postgres;

--
-- Name: gejala_penyakit_id_gejala_penyakit_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE gejala_penyakit_id_gejala_penyakit_seq OWNED BY gejala_penyakit.id_gejala_penyakit;


--
-- Name: penyakit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE penyakit (
    id_penyakit bigint NOT NULL,
    nama_penyakit character varying(50) NOT NULL,
    definisi_penyakit character varying(255) NOT NULL
);


ALTER TABLE penyakit OWNER TO postgres;

--
-- Name: penyakit_id_penyakit_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE penyakit_id_penyakit_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE penyakit_id_penyakit_seq OWNER TO postgres;

--
-- Name: penyakit_id_penyakit_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE penyakit_id_penyakit_seq OWNED BY penyakit.id_penyakit;


--
-- Name: stopword; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE stopword (
    id_stopword bigint NOT NULL,
    kata_stopword character varying(100) NOT NULL
);


ALTER TABLE stopword OWNER TO postgres;

--
-- Name: stopword_id_stopword_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE stopword_id_stopword_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE stopword_id_stopword_seq OWNER TO postgres;

--
-- Name: stopword_id_stopword_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE stopword_id_stopword_seq OWNED BY stopword.id_stopword;


--
-- Name: gejala id_gejala; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala ALTER COLUMN id_gejala SET DEFAULT nextval('gejala_id_gejala_seq'::regclass);


--
-- Name: gejala_penyakit id_gejala_penyakit; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala_penyakit ALTER COLUMN id_gejala_penyakit SET DEFAULT nextval('gejala_penyakit_id_gejala_penyakit_seq'::regclass);


--
-- Name: penyakit id_penyakit; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY penyakit ALTER COLUMN id_penyakit SET DEFAULT nextval('penyakit_id_penyakit_seq'::regclass);


--
-- Name: stopword id_stopword; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY stopword ALTER COLUMN id_stopword SET DEFAULT nextval('stopword_id_stopword_seq'::regclass);


--
-- Data for Name: gejala; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY gejala (id_gejala, nama_gejala) FROM stdin;
1	kembung
2	perut terasa penuh
3	rasa asam di mulut
4	berkeringat
5	mual
6	diare
7	nyeri perut
8	pusing
9	demam tinggi
10	mata merah
11	mata berair
12	pilek
13	bersin
14	batuk
15	hilang nafsu makan
16	ruam berwarna merah kecoklatan yang diawali dari s
17	bercak kecil berwarna putih keabu-abuan di mulut d
18	hidung tersumbat
19	hidung berair
20	sakit tenggorokan
21	tubuh terasa sakit
22	para-paru terhambat
23	kelelahan
24	nyeri lengan
25	kesemutan
26	kurang sensitif terhadap sentuhan
27	kemampuan tangan atau jari berkurang
28	lemas
29	nyeri kepala
30	kulit gatal
31	bisul berisi air
32	mata gatal
33	mata terbakar
34	kelopak mata sering menempel pada pagi hari
35	mata bengkak
36	mata nyeri
37	sensitif terhadap cahaya
38	penglihatan berkurang
39	feses encer
40	buang air besar lebih dari 2 kali sehari
41	kram perut
42	muntah
43	dehidrasi
44	mudah merasa kenyang setelah makan makanan berukur
45	bersendawa
46	sakit perut
47	sembelit
48	mengeden saat buang air besar
49	ukuran tinja besar atau sangat kecil
50	sakit perut bawah
51	kram perut bawah
52	penglihatan kabur
53	detak jantung tak teratur
54	sesak napas
55	nyeri otot
56	kulit pucat 
57	kulit kekuningan
58	bintik merah di kulit
59	nyeri sendi
60	nyeri tulang
61	nyeri bagian belakang mata
62	demam tinggi di sore hari
63	bibir pecah
64	bibir kering
65	lidah tertutup selaput putih kotor
66	ujung lidah dan tepi lidah kemerahan
67	mimisan
68	nyeri dada
69	kencing lebih sering
70	mudah haus
71	mudah lapar
72	berat badan turun
73	luka sulit sembuh
74	gatal pada di alat kelamin eksternal perempuan
75	disfungsi ereksi pada pria
76	dahak
77	batuk darah
78	berkeringat di malam hari
79	peradangan pada sendi
80	kelumpuhan pada satu sisi wajah
81	penurunan produksi air mata
82	nyeri di belakang telinga
83	telinga sensitif terhadap cahaya
84	kelopak mata tidak tertutup sempurna
85	gangguan mengecap
86	rasa tebal pada pipi atau mulut
87	garis keriput dan kening hilang
88	sakit kepala sebagian
89	nyeri kepala hebat di malam hari
90	sensitif terhadap suara
91	telinga gatal
92	telinga merah
93	keluar cairan kuning yang tidak berbau
94	benjolan kecil pada telinga
95	rasa penuh dibagian dalam telinga
96	tidak bisa tidur
97	sering menarik telinga
98	vertigo
99	keluar cairan dari telinga
100	kehilangan keseimbangan
101	telinga berdenging
102	sensasi merasa akan jatuh
103	keluar darah dari lubang hidung
104	keluar lendir dari hidung
105	nyeri wajah
108	sakit pusing
\.


--
-- Name: gejala_id_gejala_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('gejala_id_gejala_seq', 108, true);


--
-- Data for Name: gejala_penyakit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY gejala_penyakit (id_gejala_penyakit, id_penyakit, id_gejala, bobot) FROM stdin;
1	1	1	0.20000000000000001
2	1	2	0.29999999999999999
3	1	20	0.80000000000000004
4	1	4	0.5
5	1	5	0.10000000000000001
6	6	77	0.40000000000000002
7	6	11	0.90000000000000002
8	6	12	0.20000000000000001
9	6	34	0.59999999999999998
10	7	12	0.80000000000000004
11	7	35	0.10000000000000001
12	7	20	0.20000000000000001
13	7	37	0.69999999999999996
14	7	38	0.20000000000000001
\.


--
-- Name: gejala_penyakit_id_gejala_penyakit_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('gejala_penyakit_id_gejala_penyakit_seq', 14, true);


--
-- Data for Name: penyakit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY penyakit (id_penyakit, nama_penyakit, definisi_penyakit) FROM stdin;
1	muntah	muntah
2	campak	campak
3	infeksi saluran napas akut	infeksi saluran napas akut
4	sindrom terowongan karpal	sindrom terowongan karpal
5	cacar air	cacar air
6	konjungtivitas/mata merah	konjungtivitas/mata merah
7	keatitis akut	kreatitis akut
8	keputihan dalam kehamilan	keputihan dalam kehamilan
9	diare	diare
10	dispesia/maag	dispesia/maag
11	irritable Bowel Syndrome	irritable Bowel Syndrome
12	konstipasi/sembelit	konstipasi/sembelit
13	hipertensi	hipertensi
14	anemia	anemia
15	hepatitis A	hepatitits A
16	demam berdarah dengue	demam berdarah dengue
17	demam tifoid	demam tifoid
18	penyakit jantung koroner	penyakit jantung koroner
19	diabetes melitus	diabetes melitus
20	tuberkulosis	tuberkulosis
21	asam urat	asam urat
22	bells palsy	bells palsy
23	cluster type headache	cluster type headache
24	migren	migren
25	tension type headache	tension type headache
26	otitis eksterna	otitis eksterna
27	otitis media akut	otitis media akut
28	otitis media efusi	otitis media efusi
29	otitis media supuratif kronik	otitis media supuratif kronik
30	vertigo	vertigo
31	epistaksis/mimisan	epistaksis/mimisan
32	rinosinusistis	rinosinusistis
\.


--
-- Name: penyakit_id_penyakit_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('penyakit_id_penyakit_seq', 32, true);


--
-- Data for Name: stopword; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY stopword (id_stopword, kata_stopword) FROM stdin;
1	dan
2	dengan
\.


--
-- Name: stopword_id_stopword_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('stopword_id_stopword_seq', 2, true);


--
-- Name: gejala idx_16388_primary; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala
    ADD CONSTRAINT idx_16388_primary PRIMARY KEY (id_gejala);


--
-- Name: gejala_penyakit idx_16394_primary; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala_penyakit
    ADD CONSTRAINT idx_16394_primary PRIMARY KEY (id_gejala_penyakit);


--
-- Name: penyakit idx_16400_primary; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY penyakit
    ADD CONSTRAINT idx_16400_primary PRIMARY KEY (id_penyakit);


--
-- Name: stopword idx_16406_primary; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY stopword
    ADD CONSTRAINT idx_16406_primary PRIMARY KEY (id_stopword);


--
-- Name: idx_16388_id_gejala; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16388_id_gejala ON gejala USING btree (id_gejala);


--
-- Name: idx_16394_id_gejala; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16394_id_gejala ON gejala_penyakit USING btree (id_gejala);


--
-- Name: idx_16394_id_penyakit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16394_id_penyakit ON gejala_penyakit USING btree (id_penyakit);


--
-- Name: idx_16400_id_penyakit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16400_id_penyakit ON penyakit USING btree (id_penyakit);


--
-- Name: gejala_penyakit gejala_penyakit_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala_penyakit
    ADD CONSTRAINT gejala_penyakit_ibfk_1 FOREIGN KEY (id_gejala) REFERENCES gejala(id_gejala) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: gejala_penyakit gejala_penyakit_ibfk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY gejala_penyakit
    ADD CONSTRAINT gejala_penyakit_ibfk_2 FOREIGN KEY (id_penyakit) REFERENCES penyakit(id_penyakit) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

