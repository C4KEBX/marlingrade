{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;\f1\froman\fcharset0 Times-Bold;\f2\fnil\fcharset0 AppleColorEmoji;
\f3\fmodern\fcharset0 Courier;\f4\fnil\fcharset0 Menlo-Regular;\f5\froman\fcharset0 Times-Italic;
\f6\fmodern\fcharset0 Courier-Bold;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red241\green244\blue245;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;\cssrgb\c95686\c96471\c96863;}
{\*\listtable{\list\listtemplateid1\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid1\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid1}
{\list\listtemplateid2\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid101\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid2}
{\list\listtemplateid3\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid201\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid3}
{\list\listtemplateid4\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid301\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid4}
{\list\listtemplateid5\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid401\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid5}
{\list\listtemplateid6\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid501\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid6}
{\list\listtemplateid7\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid601\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid7}}
{\*\listoverridetable{\listoverride\listid1\listoverridecount0\ls1}{\listoverride\listid2\listoverridecount0\ls2}{\listoverride\listid3\listoverridecount0\ls3}{\listoverride\listid4\listoverridecount0\ls4}{\listoverride\listid5\listoverridecount0\ls5}{\listoverride\listid6\listoverridecount0\ls6}{\listoverride\listid7\listoverridecount0\ls7}}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 To deliver real-time or daily "propensity spikes" to agents without melting your database or blowing through API budgets, the system architecture needs a decoupled, asynchronous data pipeline.\
Because you are scraping Texas County Appraisal District (CAD) registries\'97which publish data updates in batches rather than live streams\'97your architecture should be built around a 
\f1\b scheduled batch-processing model
\f0\b0  that triggers an external notification engine.\
Here is the lightweight, cost-effective MVP system architecture for 
\f1\b Marlin's Spike Notification Engine
\f0\b0 .\
\
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55356 \u57303 \u65039 
\f1\b  The Data Pipeline & Processing Architecture\
\pard\pardeftab720\partightenfactor0

\f3\b0\fs26 \cf0 \cb3 [ Local Texas CADs ] (Travis, Williamson, Hays)\
        
\f4 \uc0\u9474 
\f3 \
        
\f4 \uc0\u9660 
\f3  (Scheduled Crons: Daily at 2:00 AM)\
[ Local Scraping Engine ] \
        
\f4 \uc0\u9474 
\f3 \
        
\f4 \uc0\u9660 
\f3  (Inserts Raw Records)\
[ PostgreSQL Staging Database ]\
        
\f4 \uc0\u9474 
\f3 \
        
\f4 \uc0\u9660 
\f3  (Triggers Score Calculation Engine)\
[ Marlin Grading Algorithm ] 
\f4 \uc0\u9472 \u9472 \u9472 \u9654 
\f3  Checks: Tenure, Homestead Drops, Tax Rollbacks\
        
\f4 \uc0\u9474 
\f3 \
        
\f4 \uc0\u9660 
\f3  (Detects Grade Shifts, e.g., C 
\f4 \uc0\u10132 
\f3  A)\
[ Propensity Spike Event Generator ]\
        
\f4 \uc0\u9474 
\f3 \
        
\f4 \uc0\u9660 
\f3  (Matches Zip Code to Subscribed Agents)\
[ Notification Queue (Redis) ] 
\f4 \uc0\u9472 \u9472 \u9472 \u9654 
\f3  [ Twilio API ] 
\f4 \uc0\u9472 \u9472 \u9472 \u9654 
\f3  (
\f2 \uc0\u55357 \u56561 
\f3  SMS Alert)\
                               
\f4 \uc0\u9492 \u9472 \u9472 \u9472 \u9654 
\f3  [ Resend API ] 
\f4 \uc0\u9472 \u9472 \u9472 \u9654 
\f3  (
\f2 \uc0\u55357 \u56551 
\f3  Email Alert)\
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \cb1 \
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55357 \u57056 \u65039 
\f1\b  Step-by-Step Architectural Flow\
1. The Ingestion & Diff Engine (The Scraping Layer)\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls1\ilvl0
\f1\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 How it works:
\f0\b0  Your scraping scripts run automated cron jobs nightly at 2:00 AM to pull local records.\
\ls1\ilvl0
\f1\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The Architecture:
\f0\b0  Instead of overwriting your core database, the raw data is dumped into a PostgreSQL staging table. A 
\f1\b "Diff Engine"
\f0\b0  script compares the new payload against yesterday's records to identify changes (e.g., a homestead exemption flag changing from 
\f3\fs26 \cb3 True
\f0\fs24 \cb1  to 
\f3\fs26 \cb3 False
\f0\fs24 \cb1 , or a brand new mailing address row matching an existing parcel).\
\pard\pardeftab720\sa332\partightenfactor0

\f1\b\fs40 \cf0 2. The Grading & Spike Evaluator (The Math Layer)\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls2\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 When a change is detected, the property's record passes through your core ranking script.\
\ls2\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 A 
\f1\b "Spike Event"
\f0\b0  is generated 
\f5\i only
\f0\i0  if the mathematical threshold jumps across a significant tier boundary (e.g., a home's Marlin Grade jumps from a 
\f1\b C
\f0\b0  or 
\f1\b D
\f0\b0  up to an 
\f1\b A
\f0\b0  or 
\f1\b B
\f0\b0  overnight due to a dropped homestead or an exemption rollback).\
\pard\pardeftab720\sa332\partightenfactor0

\f1\b\fs40 \cf0 3. The Multi-Tenant Subscription Matcher (The Logic Layer)\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls3\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The system takes the array of "Spike Addresses" and queries your users table:\uc0\u8232 
\f3\fs26 \cb3 SELECT agent_id FROM subscriptions WHERE active_zips CONTAINS target_zip_code;
\f0\fs24 \cb1 \
\ls3\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 This maps the high-propensity properties directly to the specific agents who "own" or track those Austin zip codes.\
\pard\pardeftab720\sa332\partightenfactor0

\f1\b\fs40 \cf0 4. The Fan-Out Notification Workers (The Delivery Layer)\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 To prevent your web server from lagging while sending thousands of notifications, offload this task to a background worker queue (like 
\f1\b BullMQ
\f0\b0  or 
\f1\b Celery
\f0\b0  backed by 
\f1\b Redis
\f0\b0 ).\
\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls4\ilvl0
\f1\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 For Low-Volume/Critical Alerts:
\f0\b0  The queue pushes a payload to 
\f1\b Twilio
\f0\b0  to dispatch a clean SMS directly to the agent's phone.\
\ls4\ilvl0
\f1\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 For Daily Bulk Digests:
\f0\b0  The queue aggregates all spikes in a zip code over 24 hours and uses a sleek transactional mail service (like 
\f1\b Resend
\f0\b0  or 
\f1\b Postmark
\f0\b0 ) to send a beautiful HTML layout.\
\pard\pardeftab720\partightenfactor0
\cf0 \
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55357 \u56561 
\f1\b  The End-User Notification Payloads\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 To keep engagement high, the actual alert templates should be minimal, high-urgency, and lead with a direct link back into the Marlin platform layout.\
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55357 \u56561 
\f1\b  SMS Text Blast (The Immediate Hook)\
\pard\pardeftab720\partightenfactor0

\fs24 \cf0 [Marlin Alert]
\f0\b0  
\f2 \uc0\u55356 \u57263 
\f0  New A+ Listing Propensity Spike detected in Zip 78702! An address on Willow St just dropped its homestead exemption after 11 years of tenure. View the full CAD analysis and pull owner info here: 
\f3\fs26 \cb3 marlin.grade/alerts/78702
\f0\fs24 \cb1 \
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55357 \u56551 
\f1\b  Daily Email Digest Header (The Morning Habit)\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls5\ilvl0
\f1\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Subject Line:
\f0\b0  
\f3\fs26 \cb3 [Marlin] 
\f2 \uc0\u9889 
\f3  14 New Real Estate Spikes in Your Austin Farm Areas
\f0\fs24 \cb1 \
\ls5\ilvl0
\f1\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The Body:
\f0\b0  A clean, dark-themed summary chart detailing how many spikes occurred per zip code, with a high-contrast 
\f1\b Signal Cyan
\f0\b0  button reading 
\f6\b\fs26 \cb3 [ Open Today's Workspace ]
\f0\b0\fs24 \cb1 .\
\pard\pardeftab720\partightenfactor0
\cf0 \
\pard\pardeftab720\sa332\partightenfactor0

\f2\fs40 \cf0 \uc0\u55357 \u56594 
\f1\b  MVP Guardrails: Throttling & Cost Management\
\pard\pardeftab720\partightenfactor0

\f0\b0\fs24 \cf0 \
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls6\ilvl0
\f1\b \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Batching is Mandatory:
\f0\b0  Never send an individual text/email for 
\f5\i every
\f0\i0  individual house that spikes. If a CAD update causes 200 homes in a single zip code to shift status at once, the agent will block your number for spamming. Group them into a single, clean notification digest.\
\ls6\ilvl0
\f1\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The "Muted Alert" State:
\f0\b0  Inside the agent settings tab, allow users to toggle notifications on or off per zip code. If they only run mailers once a month, they can turn off daily SMS alerts and opt into a single weekly Monday morning email digest instead.\
\pard\pardeftab720\partightenfactor0
\cf0 Would you like to map out:\
\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls7\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The 
\f1\b database schema design
\f0\b0  (PostgreSQL table structures) for linking properties, scores, and agent zip code claims?\
\ls7\ilvl0\kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The 
\f1\b exact message copy/template
\f0\b0  agents can use on their direct mail postcards for these newly spiked addresses?\
\pard\pardeftab720\partightenfactor0
\cf0 \
\
\
}