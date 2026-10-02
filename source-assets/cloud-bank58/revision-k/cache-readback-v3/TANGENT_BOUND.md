# Fixed positive-handed tangent precision model

The gate below is independently derived from signed-oct16 storage and float32
operation bounds. It is **not** selected from the observed dot-product maximum.
It is restricted to this SHA-fixed cache, positive handedness, ordinary IEEE
round-to-nearest arithmetic and normal finite values. It does not establish the
unknown upstream insertion call or prove an unseen prequantization tangent was
exactly perpendicular.

[Godot 4.5.1 vector3.cpp](https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/core/math/vector3.cpp)
defines the oct fold/unfold and tangent encoding. Tangent encoding clamps the
second coordinate to bias `1/32767`, maps it into a half interval, and uses the
half-interval sign as handedness. This cache has only +1 handedness; negative
handedness is rejected rather than silently applying the same bound.

Set `Q=65535`, float32 unit roundoff `u=2^-24`, and

`L(a,b) = 2 sqrt(3) sqrt(a²+b²+(a+b)²)`.

Normal stored-coordinate truncation error is at most `1/Q` per coordinate.
For positive tangents, second-coordinate bias and truncation act in opposite
directions, so the inverse-mapped error is at most
`max(1/32767, 2/Q) = 1/32767`; first-coordinate error remains `1/Q`.
Oct unfolding is continuous piecewise affine over the full square, with Euclidean
error at most `2 sqrt(a²+b²+(a+b)²)`. Crossing a fold preserves this bound by
piecewise integration. Unnormalized oct vectors have L1 norm 1 and therefore
L2 norm at least `1/sqrt(3)`; normalization adds at most the sqrt(3) factor.

Pure quantization direction-error sum is thus
`L(1/Q,1/Q)+L(1/Q,1/32767) = 0.00032725877842975683`.

Conservative standard-float32 operation budgets, independent of observed values:

- Oct encoding: at most 4u stored-coordinate error
- Quantization multiply and inverse scaling: at most 2u each, yielding 8u total
- Signed second-coordinate expansion doubles that budget and adds one rounded
  subtraction, yielding 17u
- Oct decoding contributes less than 20u direction error; one further
  normalization raises this to less than 27u, bounded by 32u per vector
- Two vector errors plus the final dot product add `64u+1024u²+8u`

With `a=1/Q+8u`, `b=1/32767+17u`, the implemented fixed gate is

`PERP_EPS = L(a,a)+L(a,b)+72u+1024u² = 0.00034205286850920414`.

Raw finite/nonzero/unit/handedness tests run first. Then N and T are each
normalized once and `abs(N dot T)` is compared with that gate. The tangent length
error is bounded by 32u direction error plus less than 6u length-evaluation error;
the fixed power-of-two envelope `64u = 0.000003814697265625` is the unit gate.

This is a **codec-model-derived semantic acceptance gate**. It covers normal
signed-oct storage precision under the stated arithmetic assumptions; it is not
claimed as a proof of every unobserved engine preprocessing step. Exact original
surface/payload SHA checks separately bind the actual stored result. The original
Godot normal unit/geometric `2e-4` and vertex `1e-5` gates are unchanged.

An independent mathematical reviewer checked the fold argument, tangent bias,
positive-sign restriction, float budget and additional normalization. The review
recommended 64u rather than the unnecessary 128u initial conservative draft.
