# tmobileBill_pdftocsv_flask
Simple flask app to let you upload all your tmobile bill statements and generates a csv file with monthly line wise bills

# To run
Install Flask - `pip3 install flask`
Run the app in local with `python3 app.py`

Note that the bill files here should be direct bill pdf exports from tmobile portals only then it will work as expected.

# Example output generated 
```
Line,Bill Period,Base charge,"Extra charges (Equipment, Services etc)",Bill Amount
(469) 325-xxxx,Nov 12 - Dec 12,$23.33,$0.00,$23.33
(469) 438-xxxx,Nov 12 - Dec 12,$23.33,$15.00,$38.33
(972) 799-xxxx,Nov 12 - Dec 12,$23.33,$45.20,$68.53
(469) 929-xxxx,Nov 12 - Dec 12,$23.33,$0.00,$23.33
(469) 325-xxxx,Dec 12 - Jan 11,$23.33,$0.00,$23.33
(469) 438-xxxx,Dec 12 - Jan 11,$23.33,$15.00,$38.33
(972) 799-xxxx,Dec 12 - Jan 11,$23.33,$45.20,$68.53
(469) 929-xxxx,Dec 12 - Jan 11,$23.33,$0.00,$23.33
```
