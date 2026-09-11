(defun c:GENERATE-MEP-BLUEPRINT ( / filepath file line tokens layer color pt-list mdb-x mdb-y tbl-x tbl-y row-y obs-min obs-max)
  (setq filepath "C:/Users/DELL/marl_project/layout_output.txt")
  
  (if (not (findfile filepath))
    (alert (strcat "Error: Could not find layout_output.txt at: " filepath))
    (progn
      ;; Clear screen
      (command "_.ERASE" (ssget "X") "")
      
      ;; Schedule Table Position
      (setq tbl-x 11000.0)
      (setq tbl-y 9000.0)
      
      ;; Draw Table Header (Added Carbon Column)
      (command "_.COLOR" "7")
      (command "_.LINE" (list tbl-x tbl-y) (list (+ tbl-x 6500.0) tbl-y) "")
      (command "_.LINE" (list tbl-x (- tbl-y 1800.0)) (list (+ tbl-x 6500.0) (- tbl-y 1800.0)) "")
      (command "_.TEXT" (list (+ tbl-x 200.0) (- tbl-y 400.0)) "200" "0" "CCT ID | DESCRIPTION | PROTECTION | CABLE | LENGTH | CARBON FOOTPRINT")
      (setq row-y (- tbl-y 800.0))
      
      (setq file (open filepath "r"))
      (while (setq line (read-line file))
        (cond
          ;; Parse MDB Panel Position
          ((wcmatch line "MDB_PANEL:*")
           (setq tokens (marl-split line ":"))
           (setq pt-list (marl-split (cadr tokens) ","))
           (setq mdb-x (distof (car pt-list)))
           (setq mdb-y (distof (cadr pt-list)))
           (command "_.COLOR" "1")
           (command "_.RECTANG" (list (- mdb-x 300.0) (- mdb-y 1500.0)) (list (+ mdb-x 300.0) (+ mdb-y 1500.0)))
           (command "_.TEXT" (list (- mdb-x 500.0) (+ mdb-y 1700.0)) "250" "0" "MDB PANEL"))

          ;; Parse Obstacle Box
          ((wcmatch line "OBSTACLE:*")
           (setq tokens (marl-split line ":"))
           (setq obs-min (marl-split (cadr tokens) ","))
           (setq obs-max (marl-split (caddr tokens) ","))
           (command "_.COLOR" "8")
           (command "_.RECTANG" 
                    (list (distof (car obs-min)) (distof (cadr obs-min))) 
                    (list (distof (car obs-max)) (distof (cadr obs-max))))
           (command "_.TEXT" 
                    (list (+ (distof (car obs-min)) 200.0) (/ (+ (distof (cadr obs-min)) (distof (cadr obs-max))) 2.0)) 
                    "250" "0" "STRUCTURAL SHAFT / OBSTACLE"))

          ;; Parse Layers & Routes
          ((wcmatch line "LAYER:*")
           (setq tokens (marl-split line ":"))
           (setq layer (cadr tokens))
           (setq color (caddr tokens))
           (command "_.COLOR" color)
           (command "_.PLINE")
           (while (and (setq line (read-line file)) (/= line "END"))
             (setq pt-list (marl-split line ","))
             (command (list (distof (car pt-list)) (distof (cadr pt-list)))))
           (command ""))

          ;; Parse Symbols
          ((wcmatch line "SYMBOL:POWER_OUTLET:*")
           (setq tokens (marl-split line ":"))
           (setq pt-list (marl-split (caddr tokens) ","))
           (setq mdb-x (distof (car pt-list)))
           (setq mdb-y (distof (cadr pt-list)))
           (command "_.COLOR" "1")
           (command "_.CIRCLE" (list mdb-x mdb-y) "250")
           (command "_.TEXT" (list (+ mdb-x 350.0) mdb-y) "200" "0" "DUPLEX SOCKET"))

          ((wcmatch line "SYMBOL:DATA_JACK:*")
           (setq tokens (marl-split line ":"))
           (setq pt-list (marl-split (caddr tokens) ","))
           (setq mdb-x (distof (car pt-list)))
           (setq mdb-y (distof (cadr pt-list)))
           (command "_.COLOR" "5")
           (command "_.CIRCLE" (list mdb-x mdb-y) "250")
           (command "_.TEXT" (list (+ mdb-x 350.0) mdb-y) "200" "0" "RJ45 DATA OUTLET"))

          ;; Parse Text Labels
          ((wcmatch line "TEXT:*")
           (setq tokens (marl-split line ":"))
           (setq layer (cadr tokens))
           (setq pt-list (marl-split (caddr tokens) ","))
           (command "_.COLOR" (if (= layer "E-POWR") "1" "5"))
           (command "_.TEXT" (list (distof (car pt-list)) (distof (cadr pt-list))) "200" "0" (cadddr tokens)))

          ;; Parse Schedule Items (With Carbon Column)
          ((wcmatch line "SCHEDULE:*")
           (setq tokens (marl-split (cadr (marl-split line ":")) ","))
           (command "_.COLOR" "7")
           (command "_.TEXT" (list (+ tbl-x 200.0) row-y) "180" "0" 
                    (strcat (car tokens) " | " (cadr tokens) " | " (caddr tokens) " | " (cadddr tokens) " | " (nth 4 tokens) " | " (nth 5 tokens)))
           (setq row-y (- row-y 300.0)))

          ;; Total Carbon Footprint Summary Row
          ((wcmatch line "TOTAL_CARBON:*")
           (setq tokens (marl-split line ":"))
           (command "_.COLOR" "3") ;; Green text for total footprint
           (command "_.TEXT" (list (+ tbl-x 200.0) (- row-y 100.0)) "200" "0" 
                    (strcat "TOTAL EMBODIED CARBON: " (cadr tokens))))
        )
      )
      (close file)
      (command "_.ZOOM" "_E")
      (princ "\n✅ MEP Blueprint Regenerated with Carbon Metrics!")
    )
  )
  (princ)
)

(defun marl-split (str del / pos lst)
  (while (setq pos (vl-string-search del str))
    (setq lst (append lst (list (substr str 1 pos))))
    (setq str (substr str (+ pos (strlen del) 1))))
  (append lst (list str))
)