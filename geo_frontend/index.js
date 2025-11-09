function foo(bar) {
  var x = [];
  for (let i = 0; i < bar; i++) {
    if (i % 2 == 0) x.push(i);
    else {
      x.push(i * 3);
    }
  }
  if (bar > 5) {
    x.push("big");
  } else x.push("small");
  return x;
}

class MyClass {
  constructor(a) {
    this.a = a || 0;
    this.b = [];
  }
  add(val) {
    for (let i = 0; i < val; i++)
      if (i % 4 == 0) this.b.push(i);
      else {
        this.b.push(i + val);
      }
  }
  dump() {
    return this.b.join(",");
  }
}

let y = foo(9);
console.log(y);
let obj = new MyClass();
obj.add(5);
console.log(obj.dump());

module.exports = { foo, MyClass };
