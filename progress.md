# Machine-Coding Curriculum Progress

Last updated: 2026-10-31

## Source of truth and scope

The learner selected [ashishps1/awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design) as the
source of truth for repository-covered requirements and solution comparisons.
This is the consolidated curriculum checked on 2026-10-30; it is not a live sync.

Coverage: 33 problem documents, 3 additional solution-only topics, 5 original-only
problems, and 9 README-linked concurrency exercises: 50 unique exercises plus
one final random mock. The original first ten problems retain their order.

Duplicates across our list and the repository are counted once: LRU Cache,
Parking Lot, Elevator System, Vending Machine, and Splitwise. Language
implementations and alternate Hotel/Concert solution folders are not new problems.
Coffee Vending Machine remains a separate variant with its own requirements.
Task Management is distinct from Job Scheduler; Pub Sub is distinct from
Notification System; Course Registration is distinct from Online Learning.

## Reference workflow

- Before each problem, read its repository requirements; before judging an
  attempted solution, inspect the relevant actual implementation, preferring Python.
- The learner still derives and writes the solution. Reveal full reference
  designs/code only when explicitly requested. Guidance switches from interviewer
  mode when the learner says "mentor help me".
- Use the reference for behavior, design comparison, complexity, and concurrency;
  equivalent correct designs need not copy its class names or list orientation.
- Flag contradictory requirements, implementation bugs, or gaps explicitly.
  Record the agreed contract rather than silently copying a contradiction.
- Original-only topics have no verified answer in this repository; label their
  briefs and review reasoning as mentor-authored.
- Concurrency exercises are linked from the README to external pages. Inclusion
  does not imply a free solution exists in this repository. If unavailable, state
  that limitation and distinguish any mentor-authored guidance.
- Save the exact reference URL and accessed version/commit when available in each
  problem's progress file when that problem begins.

## Consolidated sequence

| # | Problem | Source | Status |
| --- | --- | --- | --- |
| 1 | LRU Cache | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/lru-cache.md) + original curriculum | Completed with guidance; 4 tests pass; demo runs |
| 2 | LFU Cache | Original curriculum | Started 2026-10-31; requirement clarification |
| 3 | Parking Lot | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/parking-lot.md) + original curriculum | Not started |
| 4 | Elevator System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/elevator-system.md) + original curriculum | Not started |
| 5 | Job Scheduler | Original curriculum | Not started |
| 6 | Notification System | Original curriculum | Not started |
| 7 | Rate Limiter | Original curriculum | Not started |
| 8 | Meeting Room Scheduler | Original curriculum | Not started |
| 9 | Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/vending-machine.md) + original curriculum | Not started |
| 10 | Splitwise | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/splitwise.md) + original curriculum | Not started |
| 11 | Stack Overflow | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/stack-overflow.md) | Not started |
| 12 | Logging Framework | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/logging-framework.md) | Not started |
| 13 | Traffic Signal Control System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/traffic-signal.md) | Not started |
| 14 | Coffee Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/coffee-vending-machine.md) | Not started |
| 15 | Task Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/task-management-system.md) | Not started |
| 16 | ATM | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/atm.md) | Not started |
| 17 | LinkedIn | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/linkedin.md) | Not started |
| 18 | Tic Tac Toe | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/tic-tac-toe.md) | Not started |
| 19 | Pub Sub System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/pub-sub-system.md) | Not started |
| 20 | Car Rental System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/car-rental-system.md) | Not started |
| 21 | Online Auction System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-auction-system.md) | Not started |
| 22 | Hotel Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/hotel-management-system.md) | Not started |
| 23 | Digital Wallet Service | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/digital-wallet-service.md) | Not started |
| 24 | Airline Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/airline-management-system.md) | Not started |
| 25 | Library Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/library-management-system.md) | Not started |
| 26 | Social Network (Facebook) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/social-networking-service.md) | Not started |
| 27 | Restaurant Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/restaurant-management-system.md) | Not started |
| 28 | Concert Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/concert-ticket-booking-system.md) | Not started |
| 29 | CricInfo | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/cricinfo.md) | Not started |
| 30 | Chess | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/chess-game.md) | Not started |
| 31 | Snake and Ladder | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/snake-and-ladder.md) | Not started |
| 32 | Ride-Sharing Service (Uber) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/ride-sharing-service.md) | Not started |
| 33 | Course Registration System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/course-registration-system.md) | Not started |
| 34 | Movie Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/movie-ticket-booking-system.md) | Not started |
| 35 | Online Shopping System (Amazon) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-shopping-service.md) | Not started |
| 36 | Online Stock Brokerage System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-stock-brokerage-system.md) | Not started |
| 37 | Music Streaming Service (Spotify) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/music-streaming-service.md) | Not started |
| 38 | Food Delivery Service (Swiggy) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/food-delivery-service.md) | Not started |
| 39 | Voting System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/python/votingsystem) | Not started |
| 40 | File and Directory System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/filedirectory) | Not started |
| 41 | Online Learning Platform | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/onlinelearningplatform) | Not started |
| 42 | Print FooBar Alternately | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 43 | Print Zero Even Odd | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 44 | Fizz Buzz Multithreaded | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 45 | Building H2O Molecule | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 46 | Thread-Safe Cache with TTL | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 47 | Concurrent HashMap | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 48 | Thread-Safe Blocking Queue | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 49 | Concurrent Bloom Filter | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 50 | Multithreaded Merge Sort | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 51 | Full random machine-coding mock | Original curriculum | Not started |

## Current readiness

LRU completed with substantial pair-coding help. Independent implementation under
interview conditions is not yet demonstrated. Next scheduled problem: LFU Cache.

## Cross-problem observations

The curriculum was expanded at the learner's request on 2026-10-30. Full
reference solutions remain withheld until requested.
