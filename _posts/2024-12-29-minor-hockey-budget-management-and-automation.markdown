---
layout: post
title: "Minor Hockey Budget Management and Automation"
date: 2024-12-29 08:12:07 -0500
comments: true
categories: Hockey
tags: [budget, treasurer, hockey]
image: /images/hockey-budget/banner.png
---
> Download the [Hockey Team Budget Template](https://docs.google.com/spreadsheets/d/1QwTpalK0Zn5ddMlDOLlRwBrUQUW2S0BqZGddmaGb8x8/edit) discussed in this article
{: .prompt-tip }

I've been the treasurer for a couple minor hockey teams for the past five years, and though there are resources available to the parents that choose to assume this role on their kids' teams, if you aren't comfortable with accounting or working with spreadsheets the task can be daunting.

Every minor hockey association will make some resources available, and [Hockey Canada's MHA downloads](https://www.hockeycanada.ca/en-ca/hockey-programs/mha/downloads) currently include a minor hockey budget sheet ([XLS](https://cdn.hockeycanada.ca/hockey-canada/Hockey-Programs/MHA/downloads/minor-hockey-budget-sheets-e.xls) and [instructions](https://cdn.hockeycanada.ca/hockey-canada/Hockey-Programs/MHA/downloads/minor-hockey-budget-sheets-instructions-e.pdf)), but again, these really aren't designed to do anything more than summarize the team's finances - not track or manage them.

![](/images/hockey-budget/Pasted image 20241227113831.png)

Since team treasurers aren't only accountable to the league and their team's association, but also the parents it's important to not only have accurate accounting of revenue and expenses, but also a way to provide transparency.

The money you're handling isn't yours - it belongs to everyone on the team. If anyone has questions as to what's being spent on what or how much is left it shouldn't be hard to answer.

To try and make this easier for future team managers and treasurers I've created the following [Hockey Team Budget Template](https://docs.google.com/spreadsheets/d/1QwTpalK0Zn5ddMlDOLlRwBrUQUW2S0BqZGddmaGb8x8/edit). Feel free to download/copy/use, and if you have any feedback or questions, shoot me a message.

I'll be going into some detail below as to how you can use this spreadsheet to do the following:

- Setup the Team's Budget
- Manage Parent Payment Schedules
- Manage Revenue and Expenses
- Manage a Cash Float
- Manage Bank Transactions
- Account for Fundraising and Sponsorships
- Revise the Team's Budget

A number of [Google Sheets formulas](https://support.google.com/docs/topic/1361471?hl=en&sjid=8589949122811119968-NC) are being used across multiple sheets to provide the automation and calculations. Feel free to inspect any and modify as you like.

Note that all names in the examples were generated:
* Player names: [https://www.name-generator.org.uk/quick/](https://www.name-generator.org.uk/quick/)
* Business names: [https://randommer.io/random-business-names](https://randommer.io/random-business-names)

## Setup the Team's Budget

![](/images/hockey-budget/Pasted image 20241227130902.png)
_Figure 1: Budget_

As the team treasurer, the first thing you need to work out with the team manager and head coach is how much money the season is going to cost.

Most of the information can be copied from previous seasons, but since prices are subject to change year over year you want to always estimate high. For example, if you paid $30K the previous year you may want to bump that to $34K this year (just in case). Always try to estimate a bit high, as he parents on the team have to pay for the season and it's easier to refund extra money than it is to go back and ask for more 😉.

Each section below will match one or more of the numbered sections in _Figure 1_ above.

### (1) Figure out how much you'll need to spend

Some expenses to consider when making the budget are:

* Association fees
* Practice/game ice fees
* Jersey/Sock costs
* Referee fees
* Timekeeper fees
* Tryout fees
* Extra ice rental fees
* Tournament fees
* Goalie training
* Extra training (on-ice or off-ice) and team building
* Social budget (Christmas and end of season parties)
* Player gifts
* Police checks, coaches clinics, certification and training costs
* Trainer supplies
* Coaches apparel

Not all of these are required, but can be used as a starting point.  Under the _Expenses_ section of the **Budget** sheet, just add a new row for each line item you want to track, then copy the first line item as many times as you need

![](/images/hockey-budget/Pasted image 20241227132156.png)

As you add new rows to the _Expenses_ section, the total budget should be automatically updated on the last row of the sheet.

### (2) Figure out how much money you'll need to cover costs

Once you have your total expenses plugged in, you'll need to make sure you collect at least that much money from the parents on the team.

![](/images/hockey-budget/Pasted image 20241227155003.png)

For example, if your total expenses are $96,130.00 for the season, you'll likely want to collect at least $97,000.00.

Fundraising and sponsorships can never be guaranteed, but if the team agrees on a certain minimum threshold, plugging those values in will ensure you have enough money to cover costs.

From the example above I expect to collect $95,000.00 from the parents directly, with another $10,000.00 from sponsorship and donations, for a total budget of **$105,000.000**.

### (3-5) Updates will be automatically tracked as transactions are recorded

![](/images/hockey-budget/Pasted image 20241227155505.png)

The actual amount of money we've collected and spent will be summarized automatically based on how we record revenue and expenses on the **Transactions** sheet. We will also include details for other sources of income that may be harder to track, such as:
* Current bank balance
* Cash on hand
* Total value of outstanding (uncashed) cheques

This gives us a snapshot of our current financials at all times throughout the season. If everything is adding up correctly, the _DIFF_ field should be $0.

### (6) Expense category budgets can be automatically tracked as well

![](/images/hockey-budget/Pasted image 20241227155843.png)

We'll need to know how much money we've spent in each category as the season goes on - especially if/when we go over.

![](/images/hockey-budget/Pasted image 20241227161336.png)

Once the _Budget Left_ reaches zero, you've met or exceeded the budget. I've configured [conditional formatting rules](https://support.google.com/docs/answer/78413?hl=en&co=GENIE.Platform%3DDesktop) so it stands out a bit more that you've dropped below 50% of your budget.

## Manage Parent Payment Schedules

![](/images/hockey-budget/Pasted image 20241227161737.png)
_Figure 2: Roster_

Most (if not all) the money for the season comes from the parents on the team, so it's important to understand how much money that will be, and to keep up with payments.

Once you know how much each parent will need to pay, you can work backwards from when all fees should be due to figure out a schedule.

For our example, we'll be collecting **$6,125.00** from each family. If the team was finalized in March, and we want all fees to be collected by December, a schedule such as the following might make sense:

| ------- | ----------- |
| **June 10** | **CA$800.00**   |
| **July 10** | **CA$800.00**   |
| **Aug 10**  | **CA$1,000.00** |
| **Sep 10**  | **CA$1,000.00** |
| **Oct 10**  | **CA$1,000.00** |
| **Nov 10**  | **CA$1,000.00** |
| **Dec 10**  | **CA$525.00**   |

### (1, 5, 6, 7) Per-player payment tracking

Fill out the team roster first. Only the _Last Name_ is actually used elsewhere, and the values for _Direct Payments_, _Other Payments (Not Reimbursed)_, _Paid_, and _Reimbursements_ will be calculated for you based on what is recorded in the **Transactions** sheet.

The _Outstanding_ value will begin from what you input as _Total (Per Player Rounded)_ and subtract these transactions to help keep track of what each parent still owes.

To clarify terminology:
* _Direct Payments_: E-Transfers or cash from parents that are applied directly to player fees
* _Other Payments (Not Reimbursed)_: Costs parents cover that can be subtracted from fees (ex: they paid for pizza for the team for a social event)
* _Reimbursements_: When parents have paid _more_ than the expected fees, and you want to refund them the overage amount directly

### (2, 3, 4) Total expected revenue from parent collections

Based on what we calculated in our **Budget** sheet earlier, we were going to collect **$95,000.00** from parents, so this is imported to the _Total Expected (Imported)_ field.

We've only rostered 16 players this season, so we enter that value into the _Total Players_ field, which we divide the total expected value from to figured out the _Expected Per Player_ total.

Once again, it's easier to refund money at the end of the season than it is to ask for more money if unexpected costs occur, so round up the per-player value slightly to come up with the final _Total (Per Player Rounded)_ value you'll be collecting from parents.

This final value will then be multiplied by the number of players on the team to give you the final _Total Expected_ value.

## Manage Revenue and Expenses

![](/images/hockey-budget/Pasted image 20241228091709.png)
_Figure 3: Transactions_

The **Transactions** sheet is where day to day revenue and expenses are recorded. If everything is setup properly, just keeping this sheet updated will likely be sufficient to manage your reporting for the season.

When you setup your **Budget**, each line item under _Expenses_ will be available via the _Category_ dropdown when you want to record a transaction now.

Let's walk through some examples of recording to get a feeling for how this works.

**Example 1: Parent paid directly for team related expense**
![](/images/hockey-budget/Pasted image 20241228105045.png)

Here we can a **Preseason: Tryout Related Expenses** was recorded for **$54.00** by a member of the **Boyle** family. The _Paid By_ dropdown is populated by the _Last Name_ of each player on the **Roster** sheet.

When you specify a family under the _Paid By_ column, that payment will be deducted from that player's fees automatically. This makes it easier to keep track of how much money that family still owes towards fees if they're contributing in other ways.

**Example 2: Parent paid their monthly dues directly**
![](/images/hockey-budget/Pasted image 20241228172309.png)

When **Parent Contributions** is selected, the assumption is you're recording a direct payment towards fees. If you check off the checkbox under the _Cash?_ column, it will be recorded not only as a parent contribution, but will help keep track of your cash float.

**Example 3: Paying for an expense with a cheque**
![](/images/hockey-budget/Pasted image 20241228172543.png)

Most teams don't have access to E-Transfer out of a community (or team) account, and will need to pay for things with cheques. In this case, you just enter the cheque number in the _Chq_ column - and once the cheque has been cashed, click off the _Chq. Cashed?_ checkbox.

Under the **Budget** sheet there is a _Uncashed_ section under _Revenue_ where you can quickly see how much money you have outstanding in cheques that you haven't reconciled in your bank statement yet.

## Manage a Cash Float

![](/images/hockey-budget/Pasted image 20241228172904.png)
_Figure 4: Cash Float_

If your game officials and timekeepers are paid in cash, you'll likely need to also manage a cash float. As money comes in from parents, some of that can be requested in cash, which when recorded in the **Transactions** sheet as _Cash?_ will automatically be updated in the _Current Cash_ field on your **Cash Float** sheet.

Periodically I'll do a count, which I record as a line item broken down by each individual denomination I have in the float. If my _Total_ matches the _Current Cash_ - everything's accounted for!

## Manage Bank Transactions

![](/images/hockey-budget/Pasted image 20241229071015.png)
_Figure 5: Bank Balance_

I like to have all my teams' finances in one place, so I'll copy/paste transaction records from the online banking portal to the **Bank Balance** sheet.

![](/images/hockey-budget/Pasted image 20241229071405.png)

The last value in the _Balance_ field on this sheet is what is reflected on the **Budget** sheet's _Bank_ value (using the formula `=INDEX('Bank Balance'!D2:D,COUNTA('Bank Balance'!D2:D),1)`, for anyone that's curious).

If you're not looking to track things this granularly, the **Bank Balance** sheet can be ignored and you can just periodically copy the current balance from your bank statement directly into the _Bank_ value of the **Budget** sheet.

## Account for Fundraising and Sponsorships

![](/images/hockey-budget/Pasted image 20241229071838.png)
_Figure 6: Sponsorship & Fundraising_

Fundraising and sponsorships are a big way teams subsidize the cost of the season to take some of the financial burden off parents.

The **Sponsorship & Fundraising** sheet doesn't actually feed into any further automation, but is provided as a single location to keep track of these sources of income to make it easier to account for a lump sum you'll eventually record under the **Transactions** sheet.

## Revise the Team's Budget

When you setup the budget at the beginning of the season, you won't know exactly how much additional money you may be able to raise or how many sponsorships you'll get. There may also be some additional costs you didn't anticipate, or potentially forgot all about.

As the season goes on, if you need to revise your budget, the most important thing to take into consideration is "can we afford this" - which should be a fairly easy question to answer.

As an example, let's say we want to pay for team pictures which will cost **$850.00**. Using the **Budget** sheet, we'd do the following:

1. Add a line item under _EXPENSES_ to add a new entry for _Team Pictures_, with a _Budget_ of **$850.00**
2. Check our updated _TOTAL EXPENSES_ to make sure it's still below our _TOTAL REVENUE_

![](/images/hockey-budget/Pasted image 20241229074203.png)

I typically _italicize_ expenses that are added after the final budget has been approved so it's easier to differentiate these items.

## Conclusion

Being the team treasurer is a volunteer position that comes with a lot of responsibility. At the end of the season, you're responsible for reconciling the team's budget and paying parents back for any money that remains.

Hopefully using the template I've provided will make it a little easier to do this. If you try it out, let me know if it worked for you. I'd love to hear if this makes managing your team's finances easier 😃.