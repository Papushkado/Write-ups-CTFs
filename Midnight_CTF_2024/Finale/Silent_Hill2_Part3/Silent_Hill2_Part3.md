# Challenge : 

## Enoncé

```
James à pu intercepter des communications et des échanges entres les deux pyramid Head. 
Pourrez-vous retrouver le message initial ?
```

## Résolution 
Nous récupérons le fichier compressé suivant. (Silent_Hill_2_Part_3.7z) 
En le décompressant, nous obtenons deux fichiers : 

- une image : 
![alt text](This_is_the_end_or_no.png)

- un fichier "python" intitulé abcde.py : 
```
Foxtrot Romeo Oscar Mike  Papa India Lima  India Mike Papa Oscar Romeo Tango  India Mike Alfa Golf Echo 
India Mike Papa Oscar Romeo Tango  Charlie Oscar Delta Echo Charlie Sierra 

Delta Echo Foxtrot  Romeo Oscar Tango One Three (Tango Echo X-ray Tango ):
    Romeo Echo Tango Uniform Romeo November  Charlie Oscar Delta Echo Charlie Sierra Full stop Echo November Charlie Oscar Delta Echo (Tango Echo X-ray Tango Comma  'Romeo Oscar Tango _One Three ')


Papa November Golf  = India Mike Alfa Golf Echo Full stop Oscar Papa Echo November ("India Mike Alfa Golf Echo Full stop Papa November Golf Full stop Papa November Golf ")
Papa India X-ray Echo Lima Sierra  = Lima India Sierra Tango (Papa November Golf Full stop Golf Echo Tango Delta Alfa Tango Alfa ())
Lima Alfa Romeo Golf Comma  Hotel Alfa Uniform Tango  = Papa November Golf Full stop Sierra India Zulu Echo 


Tango Echo X-ray Tango Echo  = ""
Tango Echo X-ray Tango Echo  = Romeo Oscar Tango One Three (Tango Echo X-ray Tango Echo )
Tango Echo X-ray Tango Echo _Bravo India November  = ''Full stop Juliett Oscar India November (Foxtrot "{Oscar Romeo Delta (Charlie ):Zero Eight Bravo }" Foxtrot Oscar Romeo  Charlie  India November  Tango Echo X-ray Tango Echo )
Tango Echo X-ray Tango Echo _Bravo India November  += "Zero Zero Zero Zero Zero Zero Zero Zero "  # Mike Alfa Romeo Quebec Uniform Echo Uniform Romeo  Delta Echo  Foxtrot India November 


Papa India X-ray Echo Lima Sierra _Mike Oscar Delta India Foxtrot India Echo Sierra  = []
India November Delta Echo X-ray  = Zero 

Foxtrot Oscar Romeo  Papa India X-ray Echo Lima  India November  Papa India X-ray Echo Lima Sierra :
    Romeo Comma  Golf Comma  Bravo  = Papa India X-ray Echo Lima [:Three ]
    India Foxtrot  India November Delta Echo X-ray  < Lima Echo November (Tango Echo X-ray Tango Echo _Bravo India November ):
        
        November Echo Whiskey _Bravo  = (Bravo  & ~One ) | India November Tango (Tango Echo X-ray Tango Echo _Bravo India November [India November Delta Echo X-ray ])
        India November Delta Echo X-ray  += One 
    Echo Lima Sierra Echo :
        November Echo Whiskey _Bravo  = Bravo 
    Papa India X-ray Echo Lima Sierra _Mike Oscar Delta India Foxtrot India Echo Sierra Full stop Alfa Papa Papa Echo November Delta ((Romeo Comma  Golf Comma  November Echo Whiskey _Bravo ))


Papa November Golf Full stop Papa Uniform Tango Delta Alfa Tango Alfa (Papa India X-ray Echo Lima Sierra _Mike Oscar Delta India Foxtrot India Echo Sierra )
Papa November Golf Full stop Sierra Alfa Victor Echo ('Echo November Charlie Oscar Delta Echo Full stop Papa November Golf ')

Papa Romeo India November Tango (Foxtrot "November Oscar Uniform Victor Echo Lima Lima Echo  India Mike Alfa Golf Echo  : Echo November Charlie Oscar Delta Echo Full stop Papa November Golf ")

```

On reconnait un chiffrement utilisant l'alphabet de l'OTAN (on ne garde que les majuscules). Alors on trouve le message suivant : 

```
F R O M P I L I M P O R T I M A G E I M P O R T C O D E C S D E F R O T 1 3 T E X T R E T U R N C O D E C S FULL . E N C O D E T E X T COMMA R O T 1 3 P N G I M A G E FULL . O P E N I M A G E FULL . P N G FULL . P N G P I X E L S L I S T P N G FULL . G E T D A T A L A R G COMMA H A U T P N G FULL . S I Z E T E X T E T E X T E R O T 1 3 T E X T E T E X T E B I N FULL . J O I N F O R D C 0 8 B F O R C I N T E X T E T E X T E B I N 0 0 0 0 0 0 0 0 M A R Q U E U R D E F I N P I X E L S M O D I F I E S I N D E X 0 F O R P I X E L I N P I X E L S R COMMA G COMMA B P I X E L 3 I F I N D E X L E N T E X T E B I N N E W B B 1 I N T T E X T E B I N I N D E X I N D E X 1 E L S E N E W B B P I X E L S M O D I F I E S FULL . A P P E N D R COMMA G COMMA N E W B P N G FULL . P U T D A T A P I X E L S M O D I F I E S P N G FULL . S A V E E N C O D E FULL . P N G P R I N T F N O U V E L L E I M A G E E N C O D E FULL . P N G 

```

On devine alors qu'il s'agit d'un code python. En regardant ce qu'il fait, on remarque qu'il encode un texte dans les valeurs des bits bleus de l'image. 

test.py est mon code permettant de récupérer le message qui est : 

```
*Every step in Silent Hill 2 is a descent into the past, with James Sunderland searching for his deceased wife. 
*Keeping his sanity while exploring the foggy town becomes a challenge as haunting monsters and cryptic messages guide him. 
*Echoes of his guilt and confusion build with each disturbing encounter. 
*Just when he thinks he understands, new horrors emerge, reflecting his inner turmoil. 
*{ames meets other tormented souls, each with their own dark secrets. 
*Journeying deeper, the eerie Lakeview Hotel holds the key to the mysterious letter he received.     
*a          
*3
*y
*3
*_
*4midst 
*zealously, James must piece together his fragmented past to understand his present torment. 
*3ncounters with creatures like Pyramid Head force him to face his own capacity for violence. 
*_ltimately, the choices made by the player will determine James's fate. 
*justice or forgiveness, the ending varies, reflecting the complexity of human emotions and actions. 
*0ften considered a masterpiece, Silent Hill 2's narrative depth and psychological horror are unmatched. 
*finally, as the credits roll, the player is left to ponder the moral ambiguities and personal nightmares of James. 
*_ith each playthrough, new secrets and interpretations emerge, making Silent Hill 2 a profound experience. 
*While the town of Silent Hill may be silent, the echoes of James's journey resonate long after the game is over. 
*4vercoming the horrors, understanding the past, and coping with grief are central to the Silent Hill 2 experience. 
*vividly, the game captures the essence of psychological horror and the haunting pursuit of redemption. 
*With its complex story and deep emotional impact, Silent Hill 2 remains a landmark in video game history. 
*}earning to accept the truth, James's journey is a grim reflection of the battles everyone must face within themselves.

```

Comme le format des flags sont : MCTF{...}

On trouve en prenant la première lettre de chaque ligne : `EKEJ{Ja3y3_4z3_j0f_W4vW}`

En testant différents moyens de permutation, on se rend compte qu'il s'agit d'un codage de Vigenère. Il ne reste plus qu'à trouver la clef. 

Comme je n'avais pas d'idée j'ai testé Sillenthill ce qui donne : `MCTF{Wh3r3_4r3_y0u_E4nL}`

On y est presque, en regardant le Lore de SilentHill, la femme du héros s'appelle Mary. En conservant les majsucules / minuscules on trouve : `MCTF{Wh3r3_4r3_y0u_M4rY}`

