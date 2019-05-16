# EVM-trace-partitoiner

## Objective
The trace partitioner re-categorizes the raw traces that were sorted by block according to their contract numbers.  

## Format
Input: json traces categorized by block number

Output: json traces categorized by contract number <br>
After categorizing, for each trace entry, we add the following fields:<br>
* tx: transaction number
* parent & children: serve as pointers to other addresses. For example, assume for a trace entry e, we have e.children[0] == x. In order to find this child’s trace entry, we can navigate to traces/x, and re-find the corresponding transaction via binary search. By matching the cti (e.cti.append(0)), we can finally find the trace entry.
* serial: serial number of transactions starting from 0. It should meet the following constraints: a) All calls in one transaction always have the same serial number. b) In one block, transactions executed earlier always have smaller serial numbers. c) Transactions in an earlier block always have smaller serial numbers.

Also, we eliminate the 'address' field.


<sup>1</sup>*Note: contract creation runs distinct code, and its corresponding trace should not be mixed with its following traces. Instead, this entry should be placed in another file called 'creation.json'.*

## Examples
Input: 
```
rawtraces/00050111/txlist.json
["0x893c428fed019404f704cf4d9be977ed9ca01050ed93dccdd6c169422155586f"]  --> transaction number

rawtraces/00050111/tracelist.json
[
 [
  {
   "cti": [],
   "address": "0x109c4f2ccc82c4d77bde15f306707320294aea3f",   --> contract number
   "success": true,
   "path": [[int,int]...],
   "mrd": [[int,int,str,[[int,int,str]...]]...],
   "srd": [[int,int,str,[list<int>,int,int,str]]...]
  }
 ]
]  

```

Output: 
```
traces/0x109c4f2ccc82c4d77bde15f306707320294aea3f/creation.json   --> contract number
{
 "tx": "0xb8f2ff00ccd2db351281cff6da5dd47b4d6c87e851ff4a5168a20b68f60270ec",  --> transaction number
 "serial": int,
 "cti": [],
 "success": true,
 "parent": null,
 "children": [],
 "path": [[int,int]...],
 "mrd": [[int,int,str,[[int,int,str]...]]...],
 "srd": [[int,int,str,[list<int>,int,int,str]]...],
 "code": "0x6060604052361561001f5760e060020a6000350463..."
}

traces/0x109c4f2ccc82c4d77bde15f306707320294aea3f/0.json
[
 {
   "tx": "0x9e2783b3c42dea792faf9b636aeba0b4384bc0ec19f1a47d931ffee686869637", --> transaction number
   "serial": int,
   "cti": [],
   "success": false,
   "parent": str,
   "children": list<str>,
   "path": [[int,int]...],
   "mrd": [[int,int,str,[[int,int,str]...]]...],
   "srd": [[int,int,str,[list<int>,int,int,str]]...]
 }
 ...
]  

 ```

## Basic workflow:
* Scan all the traces
* For each trace,
    * Assign a serial number for binary search
    * Attach the parent/children references
    * Categorize into the correct contract directory
        