# Azure data factory data flow multiple join

## use case how can multiple sql select join created using data flow

## Details

Here i am considering a sql select query with 5 joins. i have one fact and 4 dimensions to join

## Tables Details

- Fact Population
- Dimension State
- Dimention Countyname
- Dimenation Race
- Dimension Sex

## Steps

- First create a pipeline
- Create a New data flow
- connect to fact first as source
- Select join 
- Configure state as another source
- Connect the join columns
- do the same for other dimenstions as below image.

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow6.jpg "Service Health")

- Once joins are created then save and publish
- Then go to pipeline and trigger once


## End to End Flow - dataflow

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow2.jpg "Service Health")

## Monitor output of data flow

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow3.jpg "Service Health")

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow4.jpg "Service Health")

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow5.jpg "Service Health")

## Log analytics metric output for ADF run above

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow7.jpg "Service Health")

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow8.jpg "Service Health")

![alt text](https://github.com/balakreshnan/Accenture/blob/master/images/adfdataflow9.jpg "Service Health")

- More to come