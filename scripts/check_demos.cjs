/* Numerical invariants independent of the page markup. */
const assert = require('node:assert/strict');
const d = require('../docs/_static/course-demos.js');
assert.ok(Math.abs(d.cdf(0)-0.5)<1e-6);
assert.ok(Math.abs(d.cdf(1.95996398454)-0.975)<1e-6);
assert.ok(Math.abs(d.tail(4)-0.00003167124)<1e-7);
const single=d.selectionP([1.96]);
assert.ok(Math.abs(single.naive-single.selective)<1e-7);
assert.equal(d.riskExperiment({kind:'uu',seed:5,n:100,delta:2,pi:.4,a:.5,b:.5}).identified,false);
const uu=d.riskExperiment({kind:'uu',seed:82,n:20000,delta:2,pi:.4,a:.85,b:.15});
const atZero=uu.corrected.find(x=>Math.abs(x[0])<1e-10)[1];
assert.ok(Math.abs(atZero-0.1586552539)<.02,'UU reconstruction should recover the symmetric Gaussian error');
const equal=d.bandit([.4,.4,.4],100,8);
assert.equal(equal.ucb.regret,0);assert.equal(equal.uniform.regret,0);
const b=d.bandit([.2,.5,.8],400,9);
assert.equal(b.ucb.counts.reduce((a,c)=>a+c,0),400);
assert.equal(b.uniform.counts.reduce((a,c)=>a+c,0),400);
assert.ok(b.ucb.points.every((x,i,a)=>i===0||x[1]>=a[i-1][1]));
const random=d.rng(204),B=20000,p=10;let rejected=0,naive=0;
for(let i=0;i<B;i++){
 const s=d.selectionP(Array.from({length:p},()=>d.normal(random)));
 assert.ok(s.selective+1e-10>=s.naive);
 rejected+=s.selective<=.05;naive+=s.naive<=.05;
}
assert.ok(Math.abs(rejected/B-.05)<.008,'selected pivot should be calibrated under the stated null');
assert.ok(Math.abs(naive/B-(1-.95**p))<.015,'naive selection inflation should match the analytic probability');
console.log('Demo numerical checks passed:',{selected_rejection:rejected/B,naive_rejection:naive/B});
