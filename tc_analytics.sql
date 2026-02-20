create database business_workflow;
use business_workflow;

create database tc_trades_db;

use tc_trades_db;
show databases;

show tables;

select * from tc_trades ; 

-- 1. asset type
select asset_type, count(*) from tc_trades group by asset_type;

-- 2. side wise
select side, count(*) from tc_trades group by side;

-- 3. option wise
select option_type from tc_trades group by option_type;

-- 4. currency wise
select issue_ccy, count(*) as cnt from tc_trades group by issue_ccy;

-- 5. record type wise
select record_type, count(*) as cnt from tc_trades group by record_type;

-- 6. pb-map type wise 
select pb_map, count(*) as cnt from tc_trades group by pb_map;

-- 7.pm wise 
select pm, count(*) as cnt from tc_trades group by pm; 

-- 8. ticker wise
select ticker, count(*) as cnt from tc_trades group by ticker;

-- 9. Data table
select 
	isin, 
	cusip, 
	account_number, 
    executing_broker, 
    settlement_date, 
    price,
    quantity,
    comm_amount, 
    net_amount
from tc_trades;
