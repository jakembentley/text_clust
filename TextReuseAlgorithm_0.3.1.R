#Author:  Jacob Meir Bentley <bentley.jacobm@gmail.com>
#         Revisions made by Joseph Bajjalieh <jbajjal2@illinois.edu> 
#Purpose: This is a program, based off of Lincoln Mullen's textreuse R 
#         program which can potentially be used identify duplicate articles.
#         It uses a combination of Jaccard Similary, Min-hashing and Local-Sensitivty Hashing
#         to identify potential duplicate articles.
#Date:    11/29/2016
#Version  0.3.1

library(tm)
library(SnowballC)
library(textreuse)
library(numbers)

#List of Prime #s below 1000
#2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 
#59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
#127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 
#191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 
#257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
#331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 
#401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 
#467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 
#563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 
#631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 
#709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 
#797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 
#877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 
#967, 971, 977, 983, 991, 997 

hashes = 240
rows <- max(primeFactors(hashes)) # rows should be a prime number in which hashes is divided evenly
bands = hashes/rows  #<- Adjust the denominator with factors of the hashes to determine the threshold.  Use the lsh_threshold function to determine the threshold
ngrams = 9   #Must be a natural number (i.e. 1, 2, 3, 4,...)

lsh_threshold(h =hashes, b = bands)

for (i in seq(from=0, to=1, by=.01)) {
j=lsh_probability(hashes, bands, s = i)
if (exists("s")==FALSE) {
s <- data.frame(j)
} else {
s  <- rbind.fill(s, data.frame(j))  
}
}
s$y = seq(from=0, to=1, by=.01)
plot(s$y, s$j, xlab="Similarity Measure", ylab="Probability", type="l")
rm(s, i, j)






ptm <- proc.time()

output$wordcount = (sapply(strsplit(output$content, " "), length))-1
output.sub = subset(output, output$wordcount > ngrams+1)
docnum <-output.sub$aid_char
rm(output)
#specify parameters for minHash function
minhash <- minhash_generator(n =hashes, seed =3552)

# preprocess texts to eliminate:
#stop words, punctuation, and set all char to lower case
output.sub$content_clean <- tolower(output.sub$content)
output.sub$content_clean <- removePunctuation(output.sub$content_clean)

#construct TextReuseCorpus which has built in minHashing
my.corpus <- TextReuseCorpus(text = as.character(output.sub$content_clean),
                             tokenizer = tokenize_ngrams,n = 9,
                             progress = TRUE,
                             minhash_func = minhash,keep_tokens = TRUE)

names(my.corpus) <- sapply(docnum,paste,collapse=";")


#Create Buckets from Corpus
buckets <- lsh(my.corpus, bands = bands, progress = TRUE)
candidates <- lsh_candidates(buckets)
compare <- lsh_compare(candidates, my.corpus, jaccard_similarity, progress = T)

compare
proc.time() -ptm
citation("textreuse")


