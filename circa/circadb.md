# 抓取CircaDB的节律基因

## 说明

本程序用于抓取http://circadb.hogeneschlab.org/query网站上的节律gene_id，本爬虫抓取了小鼠各个组织的前50页（网站限制）节律基因的ID，需要特别注意的是，为了防止网络错误造成结果确实，程序利用了一个双向队列。