select *
from information_schema.table_constraints
where table_name='valuesdud';




ALTER TABLE `valuesdud` 
ADD CONSTRAINT `number`
  FOREIGN KEY (`number`)
  REFERENCES `metersdud` (`number`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;


SELECT DISTINCT v.number 
FROM valuesdud v
LEFT JOIN metersdud m ON v.number = m.number
WHERE m.number IS NULL;
